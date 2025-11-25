"""
Persistent Storage System for WinLink
SQLite-based storage for task history, logs, and worker performance tracking
"""
import sqlite3
import json
import time
import threading
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from core.task_manager import Task, TaskStatus, TaskType

logger = logging.getLogger(__name__)

class WinLinkDatabase:
    def __init__(self, db_path: str = "data/winlink.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._ensure_db_directory()
        self._initialize_database()
        logger.info(f"Database initialized: {db_path}")
    
    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Initialize database schema"""
        with self.lock:
            with self._get_connection() as conn:
                # Tasks table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        worker_id TEXT,
                        code TEXT NOT NULL,
                        data TEXT NOT NULL,
                        result TEXT,
                        error TEXT,
                        output TEXT,
                        created_at REAL NOT NULL,
                        started_at REAL,
                        completed_at REAL,
                        execution_time REAL,
                        memory_used REAL,
                        progress INTEGER DEFAULT 0,
                        priority INTEGER DEFAULT 0
                    )
                ''')
                
                # Workers table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS workers (
                        id TEXT PRIMARY KEY,
                        ip TEXT NOT NULL,
                        port INTEGER NOT NULL,
                        first_connected_at REAL NOT NULL,
                        last_connected_at REAL,
                        last_heartbeat REAL,
                        status TEXT NOT NULL,
                        capabilities TEXT,
                        total_tasks_completed INTEGER DEFAULT 0,
                        total_execution_time REAL DEFAULT 0.0,
                        average_memory_usage REAL DEFAULT 0.0,
                        success_rate REAL DEFAULT 1.0,
                        security_features TEXT
                    )
                ''')
                
                # System logs table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        level TEXT NOT NULL,
                        component TEXT NOT NULL,
                        message TEXT NOT NULL,
                        extra_data TEXT
                    )
                ''')
                
                # Resource usage table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS resource_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        worker_id TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        cpu_percent REAL,
                        memory_percent REAL,
                        memory_available_mb REAL,
                        disk_percent REAL,
                        disk_free_gb REAL,
                        battery_percent REAL,
                        active_containers INTEGER DEFAULT 0,
                        FOREIGN KEY (worker_id) REFERENCES workers (id)
                    )
                ''')
                
                # Performance metrics table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        worker_id TEXT NOT NULL,
                        task_id TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        metric_type TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metadata TEXT,
                        FOREIGN KEY (worker_id) REFERENCES workers (id),
                        FOREIGN KEY (task_id) REFERENCES tasks (id)
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks (created_at)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_worker_id ON tasks (worker_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_workers_status ON workers (status)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_resource_usage_timestamp ON resource_usage (timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs (timestamp)')
                
                conn.commit()
                logger.info("Database schema initialized successfully")
    
    # ─── Task Management ───
    
    def save_task(self, task: Task) -> bool:
        """Save or update a task in the database"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    conn.execute('''
                        INSERT OR REPLACE INTO tasks (
                            id, type, status, worker_id, code, data, result, error, output,
                            created_at, started_at, completed_at, execution_time, 
                            memory_used, progress, priority
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        task.id,
                        task.type.value,
                        task.status.value,
                        task.worker_id,
                        task.code,
                        json.dumps(task.data),
                        json.dumps(task.result) if task.result is not None else None,
                        task.error,
                        task.output,
                        task.created_at,
                        task.started_at,
                        task.completed_at,
                        getattr(task, 'execution_time', None),
                        getattr(task, 'memory_used', None),
                        task.progress,
                        getattr(task, 'priority', 0)
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to save task {task.id}: {e}")
            return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID"""
        try:
            with self._get_connection() as conn:
                row = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
                if row:
                    return self._row_to_task(row)
                return None
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    def get_tasks(self, status: Optional[TaskStatus] = None, worker_id: Optional[str] = None, 
                  limit: int = 100, offset: int = 0) -> List[Task]:
        """Get tasks with optional filtering"""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                if worker_id:
                    query += " AND worker_id = ?"
                    params.append(worker_id)
                
                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                rows = conn.execute(query, params).fetchall()
                return [self._row_to_task(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics"""
        try:
            with self._get_connection() as conn:
                stats = {}
                
                # Basic counts
                stats['total_tasks'] = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
                stats['completed_tasks'] = conn.execute(
                    'SELECT COUNT(*) FROM tasks WHERE status = ?', 
                    (TaskStatus.COMPLETED.value,)
                ).fetchone()[0]
                stats['failed_tasks'] = conn.execute(
                    'SELECT COUNT(*) FROM tasks WHERE status = ?', 
                    (TaskStatus.FAILED.value,)
                ).fetchone()[0]
                stats['running_tasks'] = conn.execute(
                    'SELECT COUNT(*) FROM tasks WHERE status = ?', 
                    (TaskStatus.RUNNING.value,)
                ).fetchone()[0]
                
                # Success rate
                if stats['total_tasks'] > 0:
                    stats['success_rate'] = stats['completed_tasks'] / (stats['completed_tasks'] + stats['failed_tasks'])
                else:
                    stats['success_rate'] = 0.0
                
                # Average execution time
                avg_time = conn.execute(
                    'SELECT AVG(execution_time) FROM tasks WHERE status = ? AND execution_time IS NOT NULL',
                    (TaskStatus.COMPLETED.value,)
                ).fetchone()[0]
                stats['avg_execution_time'] = float(avg_time) if avg_time else 0.0
                
                # Tasks by type
                type_counts = conn.execute('''
                    SELECT type, COUNT(*) as count 
                    FROM tasks 
                    GROUP BY type
                    ORDER BY count DESC
                ''').fetchall()
                stats['tasks_by_type'] = {row[0]: row[1] for row in type_counts}
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get task statistics: {e}")
            return {}
    
    def _row_to_task(self, row) -> Task:
        """Convert database row to Task object"""
        task = Task(
            id=row['id'],
            type=TaskType(row['type']),
            code=row['code'],
            data=json.loads(row['data']),
            status=TaskStatus(row['status']),
            worker_id=row['worker_id'],
            created_at=row['created_at']
        )
        
        task.result = json.loads(row['result']) if row['result'] else None
        task.error = row['error']
        task.output = row['output']
        task.started_at = row['started_at']
        task.completed_at = row['completed_at']
        task.progress = row['progress'] or 0
        
        # Additional attributes
        if hasattr(task, 'execution_time'):
            task.execution_time = row['execution_time']
        if hasattr(task, 'memory_used'):
            task.memory_used = row['memory_used']
        if hasattr(task, 'priority'):
            task.priority = row['priority'] or 0
        
        return task
    
    # ─── Worker Management ───
    
    def save_worker(self, worker_id: str, ip: str, port: int, status: str, 
                   capabilities: List[str] = None, security_features: List[str] = None) -> bool:
        """Save or update worker information"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    now = time.time()
                    
                    # Check if worker exists
                    existing = conn.execute('SELECT id FROM workers WHERE id = ?', (worker_id,)).fetchone()
                    
                    if existing:
                        # Update existing worker
                        conn.execute('''
                            UPDATE workers SET 
                                ip = ?, port = ?, last_connected_at = ?, status = ?,
                                capabilities = ?, security_features = ?
                            WHERE id = ?
                        ''', (
                            ip, port, now, status,
                            json.dumps(capabilities or []),
                            json.dumps(security_features or []),
                            worker_id
                        ))
                    else:
                        # Insert new worker
                        conn.execute('''
                            INSERT INTO workers (
                                id, ip, port, first_connected_at, last_connected_at, 
                                status, capabilities, security_features
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            worker_id, ip, port, now, now, status,
                            json.dumps(capabilities or []),
                            json.dumps(security_features or [])
                        ))
                    
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to save worker {worker_id}: {e}")
            return False
    
    def update_worker_heartbeat(self, worker_id: str) -> bool:
        """Update worker's last heartbeat timestamp"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    conn.execute(
                        'UPDATE workers SET last_heartbeat = ? WHERE id = ?',
                        (time.time(), worker_id)
                    )
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to update heartbeat for worker {worker_id}: {e}")
            return False
    
    def get_workers(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get worker information"""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM workers"
                params = []
                
                if status:
                    query += " WHERE status = ?"
                    params.append(status)
                
                query += " ORDER BY last_connected_at DESC"
                
                rows = conn.execute(query, params).fetchall()
                workers = []
                
                for row in rows:
                    worker = dict(row)
                    worker['capabilities'] = json.loads(worker['capabilities'] or '[]')
                    worker['security_features'] = json.loads(worker['security_features'] or '[]')
                    workers.append(worker)
                
                return workers
        except Exception as e:
            logger.error(f"Failed to get workers: {e}")
            return []
    
    # ─── Resource Usage Tracking ───
    
    def save_resource_usage(self, worker_id: str, resource_data: Dict[str, Any]) -> bool:
        """Save resource usage snapshot"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    conn.execute('''
                        INSERT INTO resource_usage (
                            worker_id, timestamp, cpu_percent, memory_percent,
                            memory_available_mb, disk_percent, disk_free_gb,
                            battery_percent, active_containers
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        worker_id,
                        time.time(),
                        resource_data.get('cpu_percent'),
                        resource_data.get('memory_percent'),
                        resource_data.get('memory_available_mb'),
                        resource_data.get('disk_percent'),
                        resource_data.get('disk_free_gb'),
                        resource_data.get('battery_percent'),
                        resource_data.get('active_containers', 0)
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to save resource usage for {worker_id}: {e}")
            return False
    
    def get_resource_history(self, worker_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get resource usage history"""
        try:
            with self._get_connection() as conn:
                since = time.time() - (hours * 3600)
                rows = conn.execute('''
                    SELECT * FROM resource_usage 
                    WHERE worker_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (worker_id, since)).fetchall()
                
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get resource history for {worker_id}: {e}")
            return []
    
    # ─── System Logging ───
    
    def log_event(self, level: str, component: str, message: str, extra_data: Dict = None) -> bool:
        """Log system event"""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    conn.execute('''
                        INSERT INTO system_logs (timestamp, level, component, message, extra_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        time.time(), level, component, message,
                        json.dumps(extra_data) if extra_data else None
                    ))
                    conn.commit()
                    return True
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            return False
    
    def get_logs(self, component: Optional[str] = None, level: Optional[str] = None,
                hours: int = 24, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get system logs"""
        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM system_logs WHERE timestamp >= ?"
                params = [time.time() - (hours * 3600)]
                
                if component:
                    query += " AND component = ?"
                    params.append(component)
                
                if level:
                    query += " AND level = ?"
                    params.append(level)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                rows = conn.execute(query, params).fetchall()
                logs = []
                
                for row in rows:
                    log_entry = dict(row)
                    if log_entry['extra_data']:
                        log_entry['extra_data'] = json.loads(log_entry['extra_data'])
                    logs.append(log_entry)
                
                return logs
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    # ─── Cleanup and Maintenance ───
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, int]:
        """Clean up old data from database"""
        cleanup_stats = {'tasks': 0, 'logs': 0, 'resources': 0}
        
        try:
            cutoff_time = time.time() - (days_to_keep * 24 * 3600)
            
            with self.lock:
                with self._get_connection() as conn:
                    # Clean up old completed/failed tasks
                    cursor = conn.execute('''
                        DELETE FROM tasks 
                        WHERE completed_at < ? AND status IN (?, ?)
                    ''', (cutoff_time, TaskStatus.COMPLETED.value, TaskStatus.FAILED.value))
                    cleanup_stats['tasks'] = cursor.rowcount
                    
                    # Clean up old logs
                    cursor = conn.execute(
                        'DELETE FROM system_logs WHERE timestamp < ?',
                        (cutoff_time,)
                    )
                    cleanup_stats['logs'] = cursor.rowcount
                    
                    # Clean up old resource data
                    cursor = conn.execute(
                        'DELETE FROM resource_usage WHERE timestamp < ?',
                        (cutoff_time,)
                    )
                    cleanup_stats['resources'] = cursor.rowcount
                    
                    conn.commit()
                    
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return cleanup_stats
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self._get_connection() as conn:
                stats = {}
                
                # Table row counts
                tables = ['tasks', 'workers', 'system_logs', 'resource_usage', 'performance_metrics']
                for table in tables:
                    count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                    stats[f'{table}_count'] = count
                
                # Database file size
                if os.path.exists(self.db_path):
                    stats['db_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                return stats
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

# Global database instance
_db_instance = None
_db_lock = threading.Lock()

def get_database(db_path: str = "data/winlink.db") -> WinLinkDatabase:
    """Get global database instance (singleton pattern)"""
    global _db_instance
    
    with _db_lock:
        if _db_instance is None:
            _db_instance = WinLinkDatabase(db_path)
        return _db_instance