"""
Cross-Check Script: Verify Tasks Execute on Workers, Not Master
================================================================

This script helps you verify that tasks are executed only on worker machines.

Run this on the MASTER machine after submitting a task, and it will show you:
1. Whether TaskExecutor exists on master (it shouldn't)
2. System resource usage before and after task submission
3. Process analysis to confirm no task execution happening locally
"""

import sys
import os
import psutil
import time

# Add core to path
ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

def check_imports():
    """Check what's imported in master_ui.py"""
    print("\n" + "="*70)
    print("1. CHECKING MASTER IMPORTS")
    print("="*70)
    
    master_file = os.path.join(ROOT, "master", "master_ui.py")
    with open(master_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'TaskExecutor' in content:
        print("❌ WARNING: TaskExecutor found in master code!")
        print("   This could mean master might execute tasks locally.")
    else:
        print("✅ VERIFIED: TaskExecutor NOT imported in master_ui.py")
        print("   Master cannot execute tasks - only dispatch them.")
    
    if 'from core.task_executor import' in content:
        print("❌ WARNING: task_executor module imported in master!")
    else:
        print("✅ VERIFIED: task_executor module NOT imported in master")
    
    print("\n   Master imports found:")
    for line in content.split('\n'):
        if line.strip().startswith('from core.') or line.strip().startswith('import core.'):
            print(f"     {line.strip()}")

def check_worker_imports():
    """Check what's imported in worker_ui.py"""
    print("\n" + "="*70)
    print("2. CHECKING WORKER IMPORTS")
    print("="*70)
    
    worker_file = os.path.join(ROOT, "worker", "worker_ui.py")
    with open(worker_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'TaskExecutor' in content:
        print("✅ VERIFIED: TaskExecutor imported in worker_ui.py")
        print("   Worker CAN execute tasks - this is correct.")
    else:
        print("❌ ERROR: TaskExecutor NOT found in worker code!")
        print("   Worker cannot execute tasks - this is a problem!")
    
    if 'from core.task_executor import TaskExecutor' in content:
        print("✅ VERIFIED: task_executor module imported in worker")
        print("   Worker has execution capability.")

def monitor_cpu_usage():
    """Monitor CPU usage to detect local execution"""
    print("\n" + "="*70)
    print("3. SYSTEM RESOURCE MONITORING")
    print("="*70)
    print("\nTo verify task execution location:")
    print("1. Run this before submitting a task")
    print("2. Note the CPU and memory usage")
    print("3. Submit a CPU-intensive task")
    print("4. Watch the numbers below")
    print("\n⚠️  If CPU spikes on MASTER → task is executing locally (BAD)")
    print("✅ If CPU stays low on MASTER → task is on worker (GOOD)")
    print("\nCurrent System Resources (Master Machine):")
    print(f"  CPU Usage: {psutil.cpu_percent(interval=1)}%")
    print(f"  Memory Usage: {psutil.virtual_memory().percent}%")
    print(f"  Active Processes: {len(psutil.pids())}")

def check_architecture():
    """Verify the architecture is correct"""
    print("\n" + "="*70)
    print("4. ARCHITECTURE VERIFICATION")
    print("="*70)
    
    print("\n✅ Expected Architecture:")
    print("   Master PC: Orchestrator/Coordinator")
    print("     - Creates tasks")
    print("     - Dispatches to workers")
    print("     - Receives results")
    print("     - NO execution capability")
    print("\n   Worker PC: Compute Node")
    print("     - Receives tasks")
    print("     - Executes code")
    print("     - Returns results")
    print("     - HAS execution capability")

def run_live_monitoring():
    """Run live monitoring of CPU usage"""
    print("\n" + "="*70)
    print("5. LIVE CPU MONITORING (Press Ctrl+C to stop)")
    print("="*70)
    print("\nMonitoring CPU usage on THIS machine (Master)...")
    print("Submit a task and watch for CPU spikes:")
    print("  - No spike = Task running on worker ✅")
    print("  - Spike = Task running on master ❌")
    print()
    
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            
            if cpu > 50:
                indicator = "🔴 HIGH CPU - Possible local execution!"
            elif cpu > 20:
                indicator = "🟡 Medium CPU"
            else:
                indicator = "🟢 Low CPU - Normal (no local execution)"
            
            print(f"\r  CPU: {cpu:5.1f}% | Memory: {mem:5.1f}% | {indicator}", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    print("\n" + "="*70)
    print("WINLINK TASK EXECUTION VERIFICATION")
    print("="*70)
    print("This script verifies tasks execute ONLY on workers, NOT on master")
    
    # Run checks
    check_imports()
    check_worker_imports()
    check_architecture()
    monitor_cpu_usage()
    
    # Ask if user wants live monitoring
    print("\n" + "="*70)
    response = input("\nDo you want to run live CPU monitoring? (y/n): ")
    if response.lower() == 'y':
        print("\n📝 Instructions:")
        print("   1. Keep this window open")
        print("   2. Open WinLink Master UI")
        print("   3. Submit a CPU-intensive task (e.g., calculate primes)")
        print("   4. Watch CPU usage here on master")
        print("   5. Compare with worker's CPU usage")
        print()
        input("Press Enter when ready to start monitoring...")
        run_live_monitoring()
    
    print("\n" + "="*70)
    print("VERIFICATION COMPLETE")
    print("="*70)
    print("\n📋 Summary:")
    print("   ✅ Check the console output above")
    print("   ✅ Master should NOT have TaskExecutor")
    print("   ✅ Worker should HAVE TaskExecutor")
    print("   ✅ Master's CPU should stay low during task execution")
    print("   ✅ Worker's CPU should spike during task execution")
    print("\n🔍 Additional Verification Methods:")
    print("   1. Check console logs - look for '[WORKER hostname] 🔧 Executing'")
    print("   2. Check Task Execution Log in Worker UI")
    print("   3. Monitor Task Manager/Resource Monitor on both machines")
    print()

if __name__ == "__main__":
    main()
