#!/usr/bin/env python3
"""
WinLink Security Demo
Demonstrates the integrated security features including containerization, 
TLS encryption, authentication, and advanced scheduling.
"""

import sys
import os
import time
import logging

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import load_config
from core.database import get_database
from core.scheduler import get_scheduler, TaskPriority
from core.container_task_executor import ContainerTaskExecutor
from core.secure_network import SecureMasterNetwork
from core.security import get_security_hardening
from core.task_manager import Task, TaskType

def main():
    print("🚀 WinLink Security Demo")
    print("=" * 50)
    
    # Load configuration with all security features
    print("📋 Loading configuration...")
    config = load_config()
    
    print(f"Configuration: {config}")
    print(f"Security features: {config.get_security_features()}")
    
    # Initialize database
    print("\n💾 Initializing database...")
    db = get_database()
    
    # Log demo start
    db.log_event('INFO', 'demo', 'Security demo started', {
        'features_enabled': config.get_security_features()
    })
    
    # Initialize security hardening
    print("\n🔐 Setting up security hardening...")
    security = get_security_hardening()
    security_info = security.get_security_info()
    
    print(f"Platform: {security_info['platform']}")
    print(f"Available security features: {security_info['available_features']}")
    
    # Create secure execution environment
    if config.security['enable_containers']:
        print("\n🐳 Creating secure execution environment...")
        env_config = security.create_secure_execution_environment(
            memory_limit_mb=config.security['max_memory_mb'],
            cpu_limit_percent=config.security['max_cpu_percent']
        )
        print(f"Security restrictions applied: {env_config['restrictions_applied']}")
    
    # Initialize secure network
    print("\n🔗 Setting up secure network...")
    network = SecureMasterNetwork(
        use_tls=config.security['enable_tls'],
        auth_token_file=config.security['auth_token_file']
    )
    network.start()
    
    # Initialize task executor
    print("\n⚡ Initializing containerized task executor...")
    executor = ContainerTaskExecutor(use_containers=config.security['enable_containers'])
    
    # Initialize advanced scheduler
    print("\n📅 Starting advanced scheduler...")
    scheduler = get_scheduler()
    scheduler.start()
    
    # Demonstrate task execution with different priorities
    print("\n🎯 Creating demonstration tasks...")
    
    demo_tasks = [
        {
            'name': 'High Priority Calculation',
            'priority': TaskPriority.HIGH,
            'code': '''
# High priority mathematical computation
import math
import time

print("Starting high priority calculation...")
result = sum(math.sqrt(i) for i in range(1, 10001))
print(f"Calculated square root sum: {result:.2f}")

# Simulate some processing time
time.sleep(2)

result = {
    "task_type": "mathematical_computation",
    "square_root_sum": result,
    "processed_numbers": 10000,
    "status": "completed_successfully"
}
            ''',
            'data': {'priority_level': 'high'},
            'requirements': {'memory_mb': 256, 'capabilities': ['computation']}
        },
        {
            'name': 'Normal Priority Data Processing',
            'priority': TaskPriority.NORMAL,
            'code': '''
# Data processing task
import json
import statistics

print("Processing data set...")
numbers = data.get('numbers', list(range(1, 1001)))

# Calculate statistics
stats = {
    'count': len(numbers),
    'sum': sum(numbers),
    'mean': statistics.mean(numbers),
    'median': statistics.median(numbers),
    'std_dev': statistics.stdev(numbers) if len(numbers) > 1 else 0,
    'min': min(numbers),
    'max': max(numbers)
}

print(f"Processed {stats['count']} numbers")
print(f"Mean: {stats['mean']:.2f}, Std Dev: {stats['std_dev']:.2f}")

result = {
    "task_type": "data_processing",
    "statistics": stats,
    "data_size": len(numbers)
}
            ''',
            'data': {'numbers': list(range(1, 1001))},
            'requirements': {'memory_mb': 128}
        },
        {
            'name': 'Low Priority Text Analysis',
            'priority': TaskPriority.LOW,
            'code': '''
# Text analysis task
text = data.get('text', 'Hello world from WinLink!')

print("Analyzing text...")

# Basic text analysis
analysis = {
    'length': len(text),
    'words': len(text.split()),
    'characters': len(text),
    'characters_no_spaces': len(text.replace(' ', '')),
    'lines': text.count('\\n') + 1,
    'uppercase_chars': sum(1 for c in text if c.isupper()),
    'lowercase_chars': sum(1 for c in text if c.islower()),
    'digits': sum(1 for c in text if c.isdigit())
}

print(f"Text analysis complete: {analysis['words']} words, {analysis['characters']} characters")

result = {
    "task_type": "text_analysis",
    "analysis": analysis,
    "original_text": text[:50] + "..." if len(text) > 50 else text
}
            ''',
            'data': {'text': 'This is a sample text for analysis. It contains multiple sentences and various characters including numbers like 123 and symbols!'},
            'requirements': {'memory_mb': 64}
        }
    ]
    
    # Submit tasks to scheduler
    task_ids = []
    for demo_task in demo_tasks:
        print(f"\n📤 Submitting task: {demo_task['name']}")
        
        # Create task
        task = Task(
            id=f"demo_task_{len(task_ids) + 1}",
            type=TaskType.CUSTOM,
            code=demo_task['code'],
            data=demo_task['data']
        )
        
        # Submit with priority and requirements
        success = scheduler.submit_task(
            task, 
            priority=demo_task['priority'],
            requirements=demo_task['requirements']
        )
        
        if success:
            task_ids.append(task.id)
            print(f"✓ Task {task.id} submitted with priority {demo_task['priority'].name}")
        else:
            print(f"✗ Failed to submit task {task.id}")
    
    # Simulate a worker for demonstration
    print("\n🤖 Simulating worker execution...")
    
    # Register a simulated worker
    worker_id = "demo_worker_1"
    worker_info = {
        'cpu_percent': 25.0,
        'memory_percent': 45.0,
        'memory_available_mb': 2048.0,
        'capabilities': ['computation', 'data_analysis'],
        'security_features': ['containerization', 'tls', 'authentication']
    }
    
    scheduler.update_worker_info(worker_id, worker_info)
    print(f"✓ Worker {worker_id} registered")
    
    # Execute tasks (simulation)
    for task_id in task_ids:
        print(f"\n🔄 Executing task {task_id}...")
        
        # Get task from database
        task = db.get_task(task_id)
        if not task:
            print(f"✗ Task {task_id} not found in database")
            continue
        
        # Execute task with container security
        try:
            result = executor.execute_task(
                task.code,
                task.data,
                progress_callback=lambda p: print(f"  Progress: {p}%") if p % 25 == 0 else None,
                task_id=task_id
            )
            
            if result['success']:
                print(f"✓ Task {task_id} completed successfully")
                print(f"  Execution time: {result['execution_time']:.2f}s")
                print(f"  Memory used: {result.get('memory_used', 0):.1f}MB")
                if result.get('stdout'):
                    print(f"  Output: {result['stdout'][:100]}...")
                
                # Update task in database
                task.status = TaskStatus.COMPLETED
                task.result = result['result']
                task.completed_at = time.time()
                
            else:
                print(f"✗ Task {task_id} failed")
                print(f"  Error: {result.get('error', 'Unknown error')}")
                
                task.status = TaskStatus.FAILED
                task.error = result.get('error')
                task.completed_at = time.time()
            
            # Save updated task
            db.save_task(task)
            
            # Notify scheduler of completion
            scheduler.task_completed(task_id, worker_id, result['success'])
            
        except Exception as e:
            print(f"✗ Task execution failed: {e}")
            # Log error
            db.log_event('ERROR', 'demo', f'Task execution failed: {e}', {
                'task_id': task_id,
                'error': str(e)
            })
    
    # Show statistics
    print("\n📊 Execution Statistics")
    print("-" * 30)
    
    # Task statistics
    task_stats = db.get_task_statistics()
    print(f"Total tasks: {task_stats.get('total_tasks', 0)}")
    print(f"Completed: {task_stats.get('completed_tasks', 0)}")
    print(f"Failed: {task_stats.get('failed_tasks', 0)}")
    print(f"Success rate: {task_stats.get('success_rate', 0):.1%}")
    print(f"Average execution time: {task_stats.get('avg_execution_time', 0):.2f}s")
    
    # Scheduler statistics
    scheduler_stats = scheduler.get_scheduler_statistics()
    print(f"\nScheduler statistics:")
    print(f"Queue size: {scheduler_stats['queue']['total_queued']}")
    print(f"Active workers: {scheduler_stats['load_balancing']['active_workers']}")
    print(f"Load balancing strategy: {scheduler_stats['load_balancing']['current_strategy']}")
    
    # Database statistics
    db_stats = db.get_database_stats()
    print(f"\nDatabase statistics:")
    print(f"Tasks stored: {db_stats.get('tasks_count', 0)}")
    print(f"Workers tracked: {db_stats.get('workers_count', 0)}")
    print(f"Log entries: {db_stats.get('system_logs_count', 0)}")
    print(f"Database size: {db_stats.get('db_size_mb', 0):.2f}MB")
    
    # Show recent logs
    print("\n📋 Recent System Logs")
    print("-" * 30)
    recent_logs = db.get_logs(hours=1, limit=10)
    for log_entry in recent_logs[-5:]:  # Show last 5 entries
        timestamp = time.strftime('%H:%M:%S', time.localtime(log_entry['timestamp']))
        print(f"[{timestamp}] {log_entry['level']}: {log_entry['message']}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    
    # Stop scheduler
    scheduler.stop()
    
    # Stop network
    network.stop()
    
    # Cleanup security environment if created
    if config.security['enable_containers'] and 'env_config' in locals():
        security.cleanup_environment(env_config)
    
    # Log demo completion
    db.log_event('INFO', 'demo', 'Security demo completed successfully', {
        'tasks_executed': len(task_ids),
        'success_rate': task_stats.get('success_rate', 0)
    })
    
    print("\n✅ WinLink Security Demo completed!")
    print(f"Executed {len(task_ids)} tasks with comprehensive security features")
    print("\nSecurity features demonstrated:")
    for feature, enabled in config.get_security_features().items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")
    
    print("\n📚 For more information, see SECURITY_README.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Demo failed with error: {e}")
        logging.exception("Demo failed")
        sys.exit(1)