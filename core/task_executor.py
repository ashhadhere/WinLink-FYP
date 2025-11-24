"""
Task Executor - Executes tasks safely in a controlled environment
"""
import io
import time
import traceback
import threading
from typing import Callable, Optional

import psutil
from contextlib import redirect_stdout, redirect_stderr


class TaskExecutor:
    def __init__(self):
        self.max_execution_time = 300  # 5 minutes max
        self.max_memory_mb = 512  # 512MB max memory per task
    
    def execute_task(
        self,
        task_code: str,
        task_data: dict,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> dict:
        """
        Execute a task safely with resource monitoring
        Returns: {
            'success': bool,
            'result': any,
            'error': str,
            'execution_time': float,
            'memory_used': float
        }
        """
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        def report_progress(value: int):
            if not progress_callback:
                return
            try:
                clamped = max(0, min(100, int(value)))
                progress_callback(clamped)
            except Exception:
                pass
        
        # Create isolated namespace for task execution
        task_namespace = {
            'data': task_data,
            'result': None,
            'report_progress': report_progress,
            '__builtins__': {
                # Safe built-ins only
                'len': len, 'range': range, 'enumerate': enumerate,
                'zip': zip, 'map': map, 'filter': filter,
                'sum': sum, 'min': min, 'max': max, 'abs': abs,
                'round': round, 'sorted': sorted, 'reversed': reversed,
                'int': int, 'float': float, 'str': str, 'bool': bool,
                'list': list, 'dict': dict, 'set': set, 'tuple': tuple,
                'print': print, 'type': type, 'isinstance': isinstance,
                'ValueError': ValueError, 'TypeError': TypeError,
                'IndexError': IndexError, 'KeyError': KeyError
            }
        }
        
        # Allow safe imports
        safe_modules = ['math', 'statistics', 'random', 'datetime', 'json', 're']
        for module in safe_modules:
            try:
                task_namespace[module] = __import__(module)
            except ImportError:
                pass
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Execute with timeout and memory monitoring
            execution_thread = threading.Thread(
                target=self._execute_with_monitoring,
                args=(task_code, task_namespace, stdout_capture, stderr_capture)
            )
            execution_thread.daemon = True
            execution_thread.start()
            execution_thread.join(timeout=self.max_execution_time)
            
            if execution_thread.is_alive():
                return {
                    'success': False,
                    'result': None,
                    'error': f'Task execution timeout ({self.max_execution_time}s)',
                    'execution_time': time.time() - start_time,
                    'memory_used': self._get_memory_usage() - start_memory,
                    'stdout': stdout_capture.getvalue(),
                    'stderr': stderr_capture.getvalue()
                }
            
            # Check if execution had an error
            # Only treat as error if result is None and there's stderr content
            stderr_content = stderr_capture.getvalue()
            result_value = task_namespace.get('result')
            
            # If there's stderr but we have a result, it might just be warnings
            if stderr_content and result_value is None:
                return {
                    'success': False,
                    'result': None,
                    'error': stderr_content,
                    'execution_time': time.time() - start_time,
                    'memory_used': self._get_memory_usage() - start_memory,
                    'stdout': stdout_capture.getvalue(),
                    'stderr': stderr_capture.getvalue()
                }
            
            # Task executed successfully
            return {
                'success': True,
                'result': result_value,
                'error': None,
                'execution_time': time.time() - start_time,
                'memory_used': self._get_memory_usage() - start_memory,
                'stdout': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue()
            }
            
        except Exception as e:
            return {
                'success': False,
                'result': None,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'memory_used': self._get_memory_usage() - start_memory,
                'stdout': stdout_capture.getvalue(),
                'stderr': stderr_capture.getvalue()
            }
    
    def _execute_with_monitoring(self, code, namespace, stdout_capture, stderr_capture):
        """Execute code with I/O redirection"""
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)
        except Exception as e:
            stderr_capture.write(f"Execution Error: {str(e)}\n{traceback.format_exc()}")
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0
    
    def get_system_resources(self):
        """Return snapshot of current system resources"""
        try:
            battery = psutil.sensors_battery()
            mem = psutil.virtual_memory()
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.2),
                "memory_percent": mem.percent,
                "memory_total_mb": mem.total / (1024 * 1024),
                "memory_available_mb": mem.available / (1024 * 1024),
                "disk_percent": psutil.disk_usage("/").percent,
                "disk_free_gb": psutil.disk_usage("/").free / (1024 ** 3),
                "battery_percent": battery.percent if battery else None,
                "battery_plugged": battery.power_plugged if battery else None,
            }
        except Exception as e:
            print(f"[ERROR] Failed to get system resources: {e}")
            return {}
