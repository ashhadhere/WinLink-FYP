"""
Advanced Task Scheduler and Load Balancer for WinLink
Implements priority-based scheduling, load balancing, and worker capacity management
"""
import time
import threading
import logging
import heapq
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, field
from core.task_manager import Task, TaskStatus, TaskType
from core.database import get_database

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3
    CRITICAL = 4

class WorkerLoadMetric(Enum):
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage" 
    TASK_COUNT = "task_count"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"

@dataclass
class WorkerCapacity:
    worker_id: str
    max_concurrent_tasks: int = 5
    current_tasks: int = 0
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_available_mb: float = 0.0
    last_heartbeat: float = 0.0
    avg_task_time: float = 0.0
    success_rate: float = 1.0
    capabilities: List[str] = field(default_factory=list)
    security_features: List[str] = field(default_factory=list)
    performance_score: float = 1.0
    
    def calculate_load_score(self) -> float:
        """Calculate overall load score (lower is better)"""

        cpu_weight = 0.3
        memory_weight = 0.25
        task_weight = 0.25
        response_weight = 0.2
        
        cpu_score = self.cpu_percent / 100.0
        memory_score = self.memory_percent / 100.0
        task_score = self.current_tasks / self.max_concurrent_tasks
        response_score = min(self.avg_task_time / 60.0, 1.0)  # Normalize to 1 minute
        
        load_score = (
            cpu_score * cpu_weight +
            memory_score * memory_weight + 
            task_score * task_weight +
            response_score * response_weight
        )

        reliability_factor = max(0.1, self.success_rate)
        
        return load_score / reliability_factor
    
    def can_accept_task(self, task_requirements: Dict[str, Any] = None) -> bool:
        """Check if worker can accept a new task"""
        if self.current_tasks >= self.max_concurrent_tasks:
            return False

        if time.time() - self.last_heartbeat > 300:  # 5 minutes
            return False

        if self.cpu_percent > 90 or self.memory_percent > 90:
            return False

        if task_requirements:
            required_memory = task_requirements.get('memory_mb', 512)
            if self.memory_available_mb < required_memory:
                return False
        
        return True

@dataclass
class PriorityTask:
    task: Task
    priority: TaskPriority
    created_at: float
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """For priority queue ordering (higher priority first, then older first)"""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at

class LoadBalancer:
    def __init__(self):
        self.workers: Dict[str, WorkerCapacity] = {}
        self.lock = threading.Lock()
        self.db = get_database()

        self.strategies = {
            'round_robin': self._round_robin_strategy,
            'least_loaded': self._least_loaded_strategy,
            'performance_based': self._performance_based_strategy,
            'capability_aware': self._capability_aware_strategy
        }
        self.current_strategy = 'performance_based'
        self.round_robin_index = 0
        
        logger.info("Load balancer initialized")
    
    def register_worker(self, worker_id: str, worker_info: Dict[str, Any]):
        """Register or update worker information"""
        with self.lock:
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerCapacity(worker_id=worker_id)
            
            worker = self.workers[worker_id]
            worker.cpu_percent = worker_info.get('cpu_percent', 0.0)
            worker.memory_percent = worker_info.get('memory_percent', 0.0)
            worker.memory_available_mb = worker_info.get('memory_available_mb', 0.0)
            worker.last_heartbeat = time.time()
            worker.capabilities = worker_info.get('capabilities', [])
            worker.security_features = worker_info.get('security_features', [])

            self._update_worker_performance(worker_id)
            
            logger.debug(f"Worker {worker_id} registered/updated")
    
    def unregister_worker(self, worker_id: str):
        """Remove worker from load balancing"""
        with self.lock:
            if worker_id in self.workers:
                del self.workers[worker_id]
                logger.info(f"Worker {worker_id} unregistered")
    
    def _update_worker_performance(self, worker_id: str):
        """Update worker performance metrics from database"""
        try:

            recent_tasks = self.db.get_tasks(worker_id=worker_id, limit=20)
            
            if recent_tasks:
                completed_tasks = [t for t in recent_tasks if t.status == TaskStatus.COMPLETED]
                failed_tasks = [t for t in recent_tasks if t.status == TaskStatus.FAILED]

                total_completed = len(completed_tasks) + len(failed_tasks)
                if total_completed > 0:
                    success_rate = len(completed_tasks) / total_completed
                    self.workers[worker_id].success_rate = success_rate

                if completed_tasks:
                    exec_times = []
                    for task in completed_tasks:
                        if task.started_at and task.completed_at:
                            exec_times.append(task.completed_at - task.started_at)
                    
                    if exec_times:
                        self.workers[worker_id].avg_task_time = sum(exec_times) / len(exec_times)

                worker = self.workers[worker_id]
                performance_factors = [
                    worker.success_rate,  # Reliability
                    1.0 - min(worker.avg_task_time / 300, 1.0),  # Speed (inverse of time)
                    1.0 - worker.calculate_load_score()  # Low load
                ]
                worker.performance_score = sum(performance_factors) / len(performance_factors)
                
        except Exception as e:
            logger.warning(f"Failed to update performance for worker {worker_id}: {e}")
    
    def select_worker(self, task_requirements: Dict[str, Any] = None) -> Optional[str]:
        """Select best worker for task based on current strategy"""
        with self.lock:
            available_workers = [
                w for w in self.workers.values() 
                if w.can_accept_task(task_requirements)
            ]
            
            if not available_workers:
                logger.warning("No available workers for task assignment")
                return None
            
            strategy_func = self.strategies.get(self.current_strategy, self._performance_based_strategy)
            selected_worker = strategy_func(available_workers, task_requirements)
            
            if selected_worker:

                self.workers[selected_worker].current_tasks += 1
                logger.debug(f"Selected worker {selected_worker} using {self.current_strategy} strategy")
            
            return selected_worker
    
    def _round_robin_strategy(self, workers: List[WorkerCapacity], 
                            task_requirements: Dict[str, Any] = None) -> Optional[str]:
        """Simple round-robin worker selection"""
        if not workers:
            return None
        
        self.round_robin_index = (self.round_robin_index + 1) % len(workers)
        return workers[self.round_robin_index].worker_id
    
    def _least_loaded_strategy(self, workers: List[WorkerCapacity],
                             task_requirements: Dict[str, Any] = None) -> Optional[str]:
        """Select worker with lowest current load"""
        if not workers:
            return None
        
        best_worker = min(workers, key=lambda w: w.calculate_load_score())
        return best_worker.worker_id
    
    def _performance_based_strategy(self, workers: List[WorkerCapacity],
                                  task_requirements: Dict[str, Any] = None) -> Optional[str]:
        """Select worker based on performance score and current load"""
        if not workers:
            return None

        def score_worker(worker):
            load_score = worker.calculate_load_score()
            performance_bonus = worker.performance_score * 0.3
            return performance_bonus - load_score
        
        best_worker = max(workers, key=score_worker)
        return best_worker.worker_id
    
    def _capability_aware_strategy(self, workers: List[WorkerCapacity],
                                 task_requirements: Dict[str, Any] = None) -> Optional[str]:
        """Select worker based on capabilities and performance"""
        if not workers:
            return None
        
        required_capabilities = task_requirements.get('capabilities', []) if task_requirements else []

        capable_workers = []
        for worker in workers:
            if all(cap in worker.capabilities for cap in required_capabilities):
                capable_workers.append(worker)

        if not capable_workers:
            capable_workers = workers

        return self._performance_based_strategy(capable_workers, task_requirements)
    
    def task_completed(self, worker_id: str, success: bool = True):
        """Notify load balancer of task completion"""
        with self.lock:
            if worker_id in self.workers:
                self.workers[worker_id].current_tasks = max(0, self.workers[worker_id].current_tasks - 1)

                alpha = 0.1  # Learning rate
                current_rate = self.workers[worker_id].success_rate
                new_success = 1.0 if success else 0.0
                self.workers[worker_id].success_rate = (alpha * new_success + (1 - alpha) * current_rate)
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """Get current load balancing statistics"""
        with self.lock:
            if not self.workers:
                return {'total_workers': 0}
            
            total_workers = len(self.workers)
            active_workers = len([w for w in self.workers.values() if w.last_heartbeat > time.time() - 300])
            total_tasks = sum(w.current_tasks for w in self.workers.values())
            avg_cpu = sum(w.cpu_percent for w in self.workers.values()) / total_workers
            avg_memory = sum(w.memory_percent for w in self.workers.values()) / total_workers
            avg_performance = sum(w.performance_score for w in self.workers.values()) / total_workers
            
            return {
                'total_workers': total_workers,
                'active_workers': active_workers,
                'total_active_tasks': total_tasks,
                'avg_cpu_percent': round(avg_cpu, 2),
                'avg_memory_percent': round(avg_memory, 2),
                'avg_performance_score': round(avg_performance, 3),
                'current_strategy': self.current_strategy
            }

class AdvancedTaskScheduler:
    def __init__(self, load_balancer: LoadBalancer = None):
        self.task_queue: List[PriorityTask] = []
        self.scheduled_tasks: Dict[str, PriorityTask] = {}
        self.load_balancer = load_balancer or LoadBalancer()
        self.lock = threading.Lock()
        self.running = False
        self.scheduler_thread = None
        self.db = get_database()

        self.max_retries = 3
        self.retry_delay_base = 5.0  # seconds
        self.scheduler_interval = 1.0  # seconds
        
        logger.info("Advanced task scheduler initialized")
    
    def start(self):
        """Start the task scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the task scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        logger.info("Task scheduler stopped")
    
    def submit_task(self, task: Task, priority: TaskPriority = TaskPriority.NORMAL,
                   requirements: Dict[str, Any] = None) -> bool:
        """Submit a task for scheduling"""
        try:
            priority_task = PriorityTask(
                task=task,
                priority=priority,
                created_at=time.time(),
                requirements=requirements or {}
            )
            
            with self.lock:
                heapq.heappush(self.task_queue, priority_task)
                self.scheduled_tasks[task.id] = priority_task

            self.db.log_event(
                'INFO', 'scheduler',
                f'Task {task.id} scheduled with priority {priority.name}',
                {'task_id': task.id, 'priority': priority.name, 'requirements': requirements}
            )
            
            logger.info(f"Task {task.id} scheduled with priority {priority.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit task {task.id}: {e}")
            return False
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            with self.lock:
                if task_id in self.scheduled_tasks:
                    priority_task = self.scheduled_tasks[task_id]
                    priority_task.task.status = TaskStatus.FAILED
                    priority_task.task.error = "Task cancelled by user"
                    del self.scheduled_tasks[task_id]

                    self.db.save_task(priority_task.task)
                    
                    logger.info(f"Task {task_id} cancelled")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                self._process_task_queue()
                time.sleep(self.scheduler_interval)
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(5.0)
    
    def _process_task_queue(self):
        """Process pending tasks in the queue"""
        with self.lock:
            processed_tasks = []
            
            while self.task_queue:
                priority_task = heapq.heappop(self.task_queue)

                if priority_task.task.id not in self.scheduled_tasks:
                    continue

                selected_worker = self.load_balancer.select_worker(priority_task.requirements)
                
                if selected_worker:

                    priority_task.task.worker_id = selected_worker
                    priority_task.task.status = TaskStatus.RUNNING
                    priority_task.task.started_at = time.time()

                    del self.scheduled_tasks[priority_task.task.id]

                    self.db.save_task(priority_task.task)

                    logger.info(f"Task {priority_task.task.id} assigned to worker {selected_worker}")
                    
                else:

                    processed_tasks.append(priority_task)

            for task in processed_tasks:
                heapq.heappush(self.task_queue, task)
    
    def update_worker_info(self, worker_id: str, worker_info: Dict[str, Any]):
        """Update worker information for load balancing"""
        self.load_balancer.register_worker(worker_id, worker_info)
    
    def task_completed(self, task_id: str, worker_id: str, success: bool = True):
        """Notify scheduler of task completion"""
        self.load_balancer.task_completed(worker_id, success)

        self.db.log_event(
            'INFO', 'scheduler',
            f'Task {task_id} completed on worker {worker_id}',
            {'task_id': task_id, 'worker_id': worker_id, 'success': success}
        )
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Get current queue statistics"""
        with self.lock:
            priority_counts = {}
            for priority in TaskPriority:
                priority_counts[priority.name] = 0
            
            for priority_task in self.task_queue:
                priority_counts[priority_task.priority.name] += 1
            
            return {
                'total_queued': len(self.task_queue),
                'total_scheduled': len(self.scheduled_tasks),
                'by_priority': priority_counts,
                'scheduler_running': self.running
            }
    
    def get_scheduler_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scheduler statistics"""
        queue_stats = self.get_queue_statistics()
        load_stats = self.load_balancer.get_load_statistics()
        
        return {
            'queue': queue_stats,
            'load_balancing': load_stats,
            'uptime': time.time() if self.running else 0
        }

_scheduler_instance = None
_scheduler_lock = threading.Lock()

def get_scheduler() -> AdvancedTaskScheduler:
    """Get global scheduler instance (singleton pattern)"""
    global _scheduler_instance
    
    with _scheduler_lock:
        if _scheduler_instance is None:
            _scheduler_instance = AdvancedTaskScheduler()
        return _scheduler_instance