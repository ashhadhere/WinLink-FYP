"""
Enhanced Task Executor with Docker Container Support
Executes tasks safely in Docker containers with resource limits and isolation
"""
import io
import json
import time
import traceback
import threading
import subprocess
import tempfile
import os
import logging
from typing import Callable, Optional, Dict, Any
import docker
import psutil
from contextlib import redirect_stdout, redirect_stderr

logger = logging.getLogger(__name__)

class ContainerTaskExecutor:
    def __init__(self, use_containers=True):
        self.use_containers = use_containers
        self.max_execution_time = 300  # 5 minutes max
        self.max_memory_mb = 512  # 512MB max memory per task
        self.max_cpu_percent = 50  # 50% max CPU usage

        self.docker_image = "winlink-task-executor:latest"
        self.container_network = "task_isolation"
        
        if self.use_containers:
            try:
                self.docker_client = docker.from_env()
                self._ensure_docker_image()
                logger.info("Docker container support enabled")
            except Exception as e:
                logger.warning(f"Docker not available, falling back to direct execution: {e}")
                self.use_containers = False

        if not self.use_containers:
            from core.task_executor import TaskExecutor
            self.fallback_executor = TaskExecutor()
    
    def _ensure_docker_image(self):
        """Ensure the task executor Docker image exists"""
        try:
            self.docker_client.images.get(self.docker_image)
            logger.info(f"Docker image {self.docker_image} found")
        except docker.errors.ImageNotFound:
            logger.info(f"Building Docker image {self.docker_image}...")
            try:

                dockerfile_content = """
FROM python:3.9-slim

RUN groupadd -r taskexec && useradd -r -g taskexec taskexec

RUN apt-get update && apt-get install -y \\
    --no-install-recommends \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN echo '#!/usr/bin/env python3' > container-executor.py && \\
    echo 'import sys, json, time, traceback' >> container-executor.py && \\
    echo 'try:' >> container-executor.py && \\
    echo '    payload = json.loads(sys.stdin.read())' >> container-executor.py && \\
    echo '    code = payload["code"]' >> container-executor.py && \\
    echo '    data = payload.get("data", {})' >> container-executor.py && \\
    echo '    exec(code)' >> container-executor.py && \\
    echo '    print(json.dumps({"success": True, "result": locals().get("result")}))' >> container-executor.py && \\
    echo 'except Exception as e:' >> container-executor.py && \\
    echo '    print(json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}))' >> container-executor.py && \\
    chmod +x container-executor.py

RUN mkdir -p /app/temp && chown -R taskexec:taskexec /app

USER taskexec

WORKDIR /app

CMD ["python", "container-executor.py"]
"""

                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    dockerfile_path = os.path.join(temp_dir, 'Dockerfile')
                    with open(dockerfile_path, 'w') as f:
                        f.write(dockerfile_content)
                    
                    self.docker_client.images.build(
                        path=temp_dir,
                        dockerfile='Dockerfile',
                        tag=self.docker_image,
                        rm=True,
                        pull=True
                    )
                    
                logger.info(f"Successfully built {self.docker_image}")
                
            except Exception as e:
                logger.error(f"Failed to build Docker image: {e}")
                self.use_containers = False
    
    def execute_task(
        self,
        task_code: str,
        task_data: dict,
        progress_callback: Optional[Callable[[int], None]] = None,
        task_id: str = None
    ) -> dict:
        """
        Execute a task safely with containerization or fallback to direct execution
        """
        if not self.use_containers:
            return self.fallback_executor.execute_task(task_code, task_data, progress_callback)
        
        return self._execute_containerized_task(task_code, task_data, progress_callback, task_id)
    
    def _execute_containerized_task(
        self,
        task_code: str,
        task_data: dict,
        progress_callback: Optional[Callable[[int], None]] = None,
        task_id: str = None
    ) -> dict:
        """
        Execute task in a Docker container with full isolation
        """
        start_time = time.time()
        container = None
        
        try:

            task_payload = {
                'task_id': task_id or f"task_{int(time.time())}",
                'code': task_code,
                'data': task_data
            }

            container_config = {
                'image': self.docker_image,
                'detach': True,
                'stdin_open': True,
                'tty': False,
                'mem_limit': f"{self.max_memory_mb}m",
                'cpu_quota': int(100000 * (self.max_cpu_percent / 100)),  # CPU quota in microseconds
                'cpu_period': 100000,
                'read_only': True,
                'security_opt': [
                    'no-new-privileges:true'
                ],
                'cap_drop': ['ALL'],
                'cap_add': ['CHOWN'],  # Basic capability needed
                'user': 'taskexec:taskexec',
                'environment': {
                    'TASK_TIMEOUT': str(self.max_execution_time),
                    'MAX_MEMORY_MB': str(self.max_memory_mb),
                    'MAX_CPU_PERCENT': str(self.max_cpu_percent)
                },
                'tmpfs': {
                    '/tmp': 'rw,noexec,nosuid,nodev,size=100m'
                }
            }

            logger.info(f"Creating container for task {task_payload['task_id']}")

            import base64
            task_json = json.dumps(task_payload)
            task_b64 = base64.b64encode(task_json.encode()).decode()
            container_config['environment']['TASK_DATA_B64'] = task_b64

            container_config['command'] = [
                'python', '-c', 
                '''
import os, json, traceback, base64
try:
    task_data = base64.b64decode(os.environ["TASK_DATA_B64"]).decode()
    payload = json.loads(task_data)
    code = payload["code"]
    data = payload.get("data", {})
    exec(code)
    print(json.dumps({"success": True, "result": locals().get("result")}))
except Exception as e:
    print(json.dumps({"success": False, "error": str(e), "traceback": traceback.format_exc()}))
                '''
            ]
            
            container = self.docker_client.containers.run(**container_config)

            try:
                result = container.wait(timeout=self.max_execution_time)
                exit_code = result['StatusCode']

                logs = container.logs(stdout=True, stderr=True).decode('utf-8')

                result_lines = [line for line in logs.split('\n') if line.strip()]
                if result_lines:
                    try:

                        for line in reversed(result_lines):
                            if line.strip().startswith('{') and line.strip().endswith('}'):
                                result_data = json.loads(line.strip())
                                break
                        else:

                            result_data = {
                                'success': False,
                                'result': None,
                                'error': 'No valid result returned from container',
                                'execution_time': time.time() - start_time,
                                'memory_used': 0,
                                'stdout': logs,
                                'stderr': ''
                            }
                    except json.JSONDecodeError:
                        result_data = {
                            'success': False,
                            'result': None,
                            'error': 'Invalid JSON result from container',
                            'execution_time': time.time() - start_time,
                            'memory_used': 0,
                            'stdout': logs,
                            'stderr': ''
                        }
                else:
                    result_data = {
                        'success': False,
                        'result': None,
                        'error': 'No output from container',
                        'execution_time': time.time() - start_time,
                        'memory_used': 0,
                        'stdout': '',
                        'stderr': ''
                    }

                result_data['execution_time'] = time.time() - start_time

                if progress_callback:
                    try:
                        progress_callback(100 if result_data.get('success') else 0)
                    except Exception:
                        pass
                
                logger.info(f"Container task completed: success={result_data.get('success')}, time={result_data['execution_time']:.2f}s")
                return result_data
                
            except docker.errors.ContainerError as e:
                return {
                    'success': False,
                    'result': None,
                    'error': f'Container execution failed: {str(e)}',
                    'execution_time': time.time() - start_time,
                    'memory_used': 0,
                    'stdout': container.logs(stdout=True).decode('utf-8') if container else '',
                    'stderr': container.logs(stderr=True).decode('utf-8') if container else ''
                }
                
        except Exception as e:
            logger.error(f"Container task execution failed: {e}")
            return {
                'success': False,
                'result': None,
                'error': f'Container setup failed: {str(e)}',
                'execution_time': time.time() - start_time,
                'memory_used': 0,
                'stdout': '',
                'stderr': str(e)
            }
            
        finally:

            if container:
                try:
                    container.stop(timeout=5)
                    container.remove(force=True)
                    logger.info("Container cleaned up")
                except Exception as e:
                    logger.warning(f"Container cleanup failed: {e}")
    
    def get_system_resources(self):
        """Return snapshot of current system resources"""
        try:
            import os
            import platform
            
            battery = psutil.sensors_battery()
            mem = psutil.virtual_memory()

            if platform.system() == "Windows":
                disk_path = os.getenv("SystemDrive", "C:") + "\\"
            else:
                disk_path = "/"
            
            disk = psutil.disk_usage(disk_path)
            
            resources = {
                "cpu_percent": psutil.cpu_percent(interval=0.2),
                "memory_percent": mem.percent,
                "memory_total_mb": mem.total / (1024 * 1024),
                "memory_available_mb": mem.available / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024 ** 3),
                "battery_percent": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
                "container_support": self.use_containers,
                "active_containers": self._get_active_containers_count()
            }
            
            logger.debug(f"Resources: CPU={resources['cpu_percent']:.1f}%, RAM={resources['memory_available_mb']:.0f}MB")
            
            return resources
        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            return {}
    
    def _get_active_containers_count(self):
        """Get count of active task containers"""
        try:
            if not self.use_containers:
                return 0
            containers = self.docker_client.containers.list(
                filters={'ancestor': self.docker_image}
            )
            return len(containers)
        except Exception:
            return 0
    
    def cleanup_containers(self):
        """Clean up any stale containers"""
        try:
            if not self.use_containers:
                return
            
            containers = self.docker_client.containers.list(
                all=True,
                filters={'ancestor': self.docker_image}
            )
            
            for container in containers:
                if container.status in ['exited', 'dead']:
                    container.remove(force=True)
                    logger.info(f"Removed stale container: {container.short_id}")
            
        except Exception as e:
            logger.warning(f"Container cleanup failed: {e}")

TaskExecutor = ContainerTaskExecutor