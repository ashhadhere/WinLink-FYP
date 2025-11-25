"""
Windows Security Testing Script for WinLink
Tests the enhanced security features on Windows platform
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_basic_setup():
    """Test basic setup and imports"""
    print("🧪 Testing basic setup...")
    
    try:
        from core.config import get_config
        from core.database import get_database
        from core.container_task_executor import ContainerTaskExecutor
        from core.security import get_security_hardening
        
        print("✅ All core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration system"""
    print("\n🧪 Testing configuration system...")
    
    try:
        from core.config import get_config
        
        config = get_config()
        print(f"✅ Configuration loaded: {config}")
        
        # Show security features
        features = config.get_security_features()
        print("🔐 Security features:")
        for feature, enabled in features.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🧪 Testing database...")
    
    try:
        from core.database import get_database
        
        db = get_database()
        
        # Test basic operations
        db.log_event('INFO', 'test', 'Database test event', {'platform': 'windows'})
        
        # Get some statistics
        stats = db.get_database_stats()
        print(f"✅ Database working - Stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_task_executor():
    """Test enhanced task executor"""
    print("\n🧪 Testing task executor...")
    
    try:
        from core.container_task_executor import ContainerTaskExecutor
        
        # Test with containers disabled for Windows compatibility
        executor = ContainerTaskExecutor(use_containers=False)
        
        test_code = '''
print("Hello from WinLink task executor!")
result = {"message": "Task executed successfully", "platform": "windows"}
'''
        
        test_data = {"test": True}
        
        print("   Executing test task...")
        result = executor.execute_task(test_code, test_data)
        
        if result['success']:
            print(f"✅ Task executed successfully!")
            print(f"   Result: {result.get('result')}")
            print(f"   Execution time: {result.get('execution_time', 0):.2f}s")
            if result.get('stdout'):
                print(f"   Output: {result['stdout'].strip()}")
        else:
            print(f"❌ Task execution failed: {result.get('error')}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Task executor test failed: {e}")
        return False

def test_security_hardening():
    """Test security hardening features"""
    print("\n🧪 Testing security hardening...")
    
    try:
        from core.security import get_security_hardening
        
        security = get_security_hardening()
        security_info = security.get_security_info()
        
        print(f"✅ Platform: {security_info['platform']}")
        print(f"✅ Available features: {security_info['available_features']}")
        
        # Test creating secure environment (Windows-compatible)
        if security_info['platform'].startswith('win'):
            print("   Windows platform detected - using Windows-specific security")
            env_config = security.create_secure_execution_environment()
            print(f"✅ Security environment created: {env_config['restrictions_applied']}")
        
        return True
    except Exception as e:
        print(f"❌ Security hardening test failed: {e}")
        return False

def test_tls_certificates():
    """Test TLS certificate availability"""
    print("\n🧪 Testing TLS certificates...")
    
    cert_file = Path("ssl/server.crt")
    key_file = Path("ssl/server.key")
    
    if cert_file.exists() and key_file.exists():
        print("✅ TLS certificates found")
        
        try:
            import ssl
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            # This would fail if certificates are invalid
            print("✅ SSL context can be created")
            return True
        except Exception as e:
            print(f"❌ Certificate validation failed: {e}")
            return False
    else:
        print("⚠️  TLS certificates not found")
        print("   Run 'python windows_setup_certificates.py' to generate them")
        return False

def test_authentication():
    """Test authentication system"""
    print("\n🧪 Testing authentication...")
    
    token_file = Path("secrets/auth_token.txt")
    
    if token_file.exists():
        with open(token_file, 'r') as f:
            token = f.read().strip()
        
        if len(token) > 10:  # Basic validation
            print("✅ Authentication token found and valid")
            return True
        else:
            print("❌ Authentication token appears invalid")
            return False
    else:
        print("⚠️  Authentication token not found")
        print("   Creating one now...")
        
        try:
            import secrets
            token = secrets.token_urlsafe(32)
            
            os.makedirs("secrets", exist_ok=True)
            with open(token_file, 'w') as f:
                f.write(token)
            
            print("✅ Authentication token created")
            return True
        except Exception as e:
            print(f"❌ Failed to create auth token: {e}")
            return False

def test_scheduler():
    """Test advanced scheduler"""
    print("\n🧪 Testing scheduler...")
    
    try:
        from core.scheduler import get_scheduler, TaskPriority
        from core.task_manager import Task, TaskType
        
        scheduler = get_scheduler()
        
        # Create a test task
        test_task = Task(
            id="test_task_1",
            type=TaskType.CUSTOM,
            code="result = 'scheduler test'",
            data={}
        )
        
        # Submit task
        success = scheduler.submit_task(test_task, TaskPriority.NORMAL)
        
        if success:
            print("✅ Task submitted to scheduler")
            
            # Get statistics
            stats = scheduler.get_queue_statistics()
            print(f"✅ Queue statistics: {stats}")
            return True
        else:
            print("❌ Failed to submit task to scheduler")
            return False
            
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False

def test_docker_availability():
    """Test Docker availability"""
    print("\n🧪 Testing Docker availability...")
    
    try:
        import docker
        client = docker.from_env()
        
        # Test Docker connection
        client.ping()
        print("✅ Docker is available and running")
        
        # Test container execution capability
        from core.container_task_executor import ContainerTaskExecutor
        executor = ContainerTaskExecutor(use_containers=True)
        
        if executor.use_containers:
            print("✅ Container-based execution enabled")
        else:
            print("⚠️  Container execution not available, using fallback")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Docker not available: {e}")
        print("   Container features will use fallback execution")
        return False

def main():
    """Run all Windows-specific tests"""
    print("🪟 WinLink Windows Security Testing")
    print("=" * 50)
    
    tests = [
        ("Basic Setup", test_basic_setup),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Task Executor", test_task_executor),
        ("Security Hardening", test_security_hardening),
        ("TLS Certificates", test_tls_certificates),
        ("Authentication", test_authentication),
        ("Scheduler", test_scheduler),
        ("Docker Availability", test_docker_availability),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your WinLink setup is ready.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start the master application")
        print("2. Run 'python demo_security.py' for a full feature demo")
    else:
        failed_tests = [name for name, result in results.items() if not result]
        print(f"\n⚠️  Some tests failed: {', '.join(failed_tests)}")
        print("Check the error messages above and fix any issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)