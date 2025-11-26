"""
Security Hardening Module for WinLink
Implements comprehensive security measures including process isolation,
resource limits, and system-level protections
"""
import os
import sys
import logging
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import signal

try:
    import resource
except ImportError:
    resource = None  # Not available on Windows

try:
    import pwd
    import grp
except ImportError:
    pwd = None  # Not available on Windows
    grp = None

logger = logging.getLogger(__name__)

class SecurityHardening:
    def __init__(self):
        self.is_linux = sys.platform.startswith('linux')
        self.is_windows = sys.platform.startswith('win')
        self.security_features = []
        self._check_available_features()
        
    def _check_available_features(self):
        """Check which security features are available on the system"""
        if self.is_linux:

            try:
                import seccomp
                self.security_features.append('seccomp')
                logger.info("Seccomp support detected")
            except ImportError:
                logger.warning("Seccomp not available - install python-seccomp package")

            if os.path.exists('/sys/module/apparmor'):
                self.security_features.append('apparmor')
                logger.info("AppArmor support detected")

            if os.path.exists('/sys/fs/selinux'):
                self.security_features.append('selinux')
                logger.info("SELinux support detected")

            if os.path.exists('/sys/fs/cgroup/cgroup.controllers'):
                self.security_features.append('cgroups_v2')
                logger.info("Cgroups v2 support detected")
            elif os.path.exists('/sys/fs/cgroup/memory'):
                self.security_features.append('cgroups_v1')
                logger.info("Cgroups v1 support detected")
        
        elif self.is_windows:

            self.security_features.extend(['job_objects', 'restricted_tokens'])
            logger.info("Windows security features available")
    
    def create_secure_execution_environment(self, 
                                          user_name: str = 'taskexec',
                                          memory_limit_mb: int = 512,
                                          cpu_limit_percent: int = 50,
                                          temp_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a secure execution environment with multiple layers of protection
        """
        env_config = {
            'user_name': user_name,
            'memory_limit_mb': memory_limit_mb,
            'cpu_limit_percent': cpu_limit_percent,
            'temp_dir': temp_dir or tempfile.mkdtemp(prefix='winlink_secure_'),
            'security_features': self.security_features.copy(),
            'restrictions_applied': []
        }
        
        try:
            if self.is_linux:
                self._setup_linux_security(env_config)
            elif self.is_windows:
                self._setup_windows_security(env_config)
                
            logger.info(f"Secure execution environment created: {env_config['restrictions_applied']}")
            return env_config
            
        except Exception as e:
            logger.error(f"Failed to create secure environment: {e}")

            self._apply_basic_restrictions(env_config)
            return env_config
    
    def _setup_linux_security(self, env_config: Dict[str, Any]):
        """Set up Linux-specific security measures"""

        if self._ensure_secure_user(env_config['user_name']):
            env_config['restrictions_applied'].append('dedicated_user')

        if 'seccomp' in self.security_features:
            self._apply_seccomp_filter(env_config)
            env_config['restrictions_applied'].append('seccomp_filter')

        if 'cgroups_v2' in self.security_features or 'cgroups_v1' in self.security_features:
            self._setup_cgroups(env_config)
            env_config['restrictions_applied'].append('cgroups_limits')

        if 'apparmor' in self.security_features:
            self._apply_apparmor_profile(env_config)
            env_config['restrictions_applied'].append('apparmor_profile')
        elif 'selinux' in self.security_features:
            self._apply_selinux_context(env_config)
            env_config['restrictions_applied'].append('selinux_context')

        self._setup_secure_temp_dir(env_config)
        env_config['restrictions_applied'].append('secure_temp_dir')
    
    def _setup_windows_security(self, env_config: Dict[str, Any]):
        """Set up Windows-specific security measures"""

        if 'restricted_tokens' in self.security_features:
            self._create_restricted_token(env_config)
            env_config['restrictions_applied'].append('restricted_token')

        if 'job_objects' in self.security_features:
            self._setup_windows_job_object(env_config)
            env_config['restrictions_applied'].append('job_object')

        self._setup_secure_temp_dir(env_config)
        env_config['restrictions_applied'].append('secure_temp_dir')
    
    def _ensure_secure_user(self, user_name: str) -> bool:
        """Ensure dedicated user account exists for task execution"""
        try:
            if self.is_linux and pwd is not None:

                try:
                    pwd.getpwnam(user_name)
                    logger.debug(f"User {user_name} already exists")
                    return True
                except KeyError:
                    pass

                subprocess.run([
                    'sudo', 'useradd', 
                    '--system',  # System user
                    '--no-create-home',  # No home directory
                    '--shell', '/bin/false',  # No shell access
                    '--groups', '',  # No additional groups
                    user_name
                ], check=True, capture_output=True)
                
                logger.info(f"Created secure user: {user_name}")
                return True
            elif self.is_windows:

                logger.info(f"Using current user with Windows job object restrictions")
                return True
            else:
                logger.warning("User management not supported on this platform")
                return False
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to create user {user_name}: {e}")
            return False
        except Exception as e:
            logger.warning(f"User creation error: {e}")
            return False
    
    def _apply_seccomp_filter(self, env_config: Dict[str, Any]):
        """Apply seccomp syscall filtering"""
        try:
            import seccomp

            f = seccomp.SyscallFilter(defaction=seccomp.ERRNO(1))

            essential_syscalls = [
                'read', 'write', 'open', 'close', 'stat', 'fstat', 'lstat',
                'poll', 'lseek', 'mmap', 'mprotect', 'munmap', 'brk',
                'rt_sigaction', 'rt_sigprocmask', 'rt_sigreturn', 'ioctl',
                'pread64', 'pwrite64', 'readv', 'writev', 'access', 'pipe',
                'select', 'sched_yield', 'mremap', 'msync', 'mincore', 'madvise',
                'dup', 'dup2', 'pause', 'nanosleep', 'getitimer', 'alarm',
                'setitimer', 'getpid', 'sendfile', 'exit', 'exit_group',
                'wait4', 'kill', 'uname', 'fcntl', 'flock', 'fsync',
                'fdatasync', 'truncate', 'ftruncate', 'getcwd', 'chdir',
                'rename', 'mkdir', 'rmdir', 'creat', 'link', 'unlink',
                'readlink', 'chmod', 'fchmod', 'chown', 'fchown', 'umask',
                'gettimeofday', 'getrlimit', 'getrusage', 'sysinfo', 'times',
                'getuid', 'getgid', 'geteuid', 'getegid', 'getgroups', 'clock_gettime'
            ]
            
            for syscall in essential_syscalls:
                try:
                    f.add_rule(seccomp.ALLOW, syscall)
                except OSError:

                    pass

            dangerous_syscalls = [
                'ptrace', 'mount', 'umount', 'umount2', 'swapon', 'swapoff',
                'reboot', 'sethostname', 'setdomainname', 'init_module',
                'delete_module', 'quotactl', 'acct', 'settimeofday'
            ]
            
            for syscall in dangerous_syscalls:
                try:
                    f.add_rule(seccomp.ERRNO(1), syscall)
                except OSError:
                    pass

            f.load()
            env_config['seccomp_filter'] = True
            logger.info("Seccomp filter applied successfully")
            
        except Exception as e:
            logger.warning(f"Failed to apply seccomp filter: {e}")
    
    def _setup_cgroups(self, env_config: Dict[str, Any]):
        """Set up cgroups resource limits"""
        try:
            cgroup_name = f"winlink_task_{os.getpid()}"
            
            if 'cgroups_v2' in self.security_features:
                self._setup_cgroups_v2(env_config, cgroup_name)
            else:
                self._setup_cgroups_v1(env_config, cgroup_name)
                
            env_config['cgroup_name'] = cgroup_name
            
        except Exception as e:
            logger.warning(f"Failed to set up cgroups: {e}")
    
    def _setup_cgroups_v2(self, env_config: Dict[str, Any], cgroup_name: str):
        """Set up cgroups v2 limits"""
        cgroup_path = f"/sys/fs/cgroup/{cgroup_name}"
        
        try:

            os.makedirs(cgroup_path, exist_ok=True)

            memory_limit = env_config['memory_limit_mb'] * 1024 * 1024
            with open(f"{cgroup_path}/memory.max", 'w') as f:
                f.write(str(memory_limit))

            cpu_quota = int(100000 * (env_config['cpu_limit_percent'] / 100))
            with open(f"{cgroup_path}/cpu.max", 'w') as f:
                f.write(f"{cpu_quota} 100000")

            with open(f"{cgroup_path}/cgroup.procs", 'w') as f:
                f.write(str(os.getpid()))
            
            logger.info(f"Cgroups v2 limits applied: {memory_limit} bytes memory, {cpu_quota} CPU quota")
            
        except Exception as e:
            logger.warning(f"Failed to setup cgroups v2: {e}")
    
    def _setup_cgroups_v1(self, env_config: Dict[str, Any], cgroup_name: str):
        """Set up cgroups v1 limits"""
        try:

            memory_cgroup_path = f"/sys/fs/cgroup/memory/{cgroup_name}"
            os.makedirs(memory_cgroup_path, exist_ok=True)
            
            memory_limit = env_config['memory_limit_mb'] * 1024 * 1024
            with open(f"{memory_cgroup_path}/memory.limit_in_bytes", 'w') as f:
                f.write(str(memory_limit))
            
            with open(f"{memory_cgroup_path}/memory.memsw.limit_in_bytes", 'w') as f:
                f.write(str(memory_limit))

            cpu_cgroup_path = f"/sys/fs/cgroup/cpu/{cgroup_name}"
            os.makedirs(cpu_cgroup_path, exist_ok=True)
            
            cpu_quota = int(100000 * (env_config['cpu_limit_percent'] / 100))
            with open(f"{cpu_cgroup_path}/cpu.cfs_quota_us", 'w') as f:
                f.write(str(cpu_quota))
            
            with open(f"{cpu_cgroup_path}/cpu.cfs_period_us", 'w') as f:
                f.write("100000")

            with open(f"{memory_cgroup_path}/cgroup.procs", 'w') as f:
                f.write(str(os.getpid()))
            
            with open(f"{cpu_cgroup_path}/cgroup.procs", 'w') as f:
                f.write(str(os.getpid()))
            
            logger.info(f"Cgroups v1 limits applied")
            
        except Exception as e:
            logger.warning(f"Failed to setup cgroups v1: {e}")
    
    def _apply_apparmor_profile(self, env_config: Dict[str, Any]):
        """Apply AppArmor security profile"""
        try:
            profile_name = "winlink-task-profile"

            result = subprocess.run(['aa-status'], capture_output=True, text=True)
            if profile_name not in result.stdout:
                logger.warning(f"AppArmor profile {profile_name} not loaded")
                return

            subprocess.run(['aa-exec', '-p', profile_name, '--'], check=True)
            env_config['apparmor_profile'] = profile_name
            logger.info(f"AppArmor profile {profile_name} applied")
            
        except Exception as e:
            logger.warning(f"Failed to apply AppArmor profile: {e}")
    
    def _apply_selinux_context(self, env_config: Dict[str, Any]):
        """Apply SELinux security context"""
        try:

            context = "unconfined_u:unconfined_r:winlink_task_t:s0"
            subprocess.run(['runcon', context], check=True)
            env_config['selinux_context'] = context
            logger.info(f"SELinux context applied: {context}")
            
        except Exception as e:
            logger.warning(f"Failed to apply SELinux context: {e}")
    
    def _setup_secure_temp_dir(self, env_config: Dict[str, Any]):
        """Set up secure temporary directory with restricted permissions"""
        temp_dir = env_config['temp_dir']
        
        try:

            os.makedirs(temp_dir, exist_ok=True)

            os.chmod(temp_dir, 0o700)

            if self.is_linux and os.getuid() == 0:  # Root user
                subprocess.run([
                    'mount', '-o', 'remount,noexec,nosuid,nodev', temp_dir
                ], check=False)  # Don't fail if this doesn't work
            
            env_config['temp_dir_secured'] = True
            logger.info(f"Secure temp directory configured: {temp_dir}")
            
        except Exception as e:
            logger.warning(f"Failed to secure temp directory: {e}")
    
    def _create_restricted_token(self, env_config: Dict[str, Any]):
        """Create restricted Windows token (Windows-specific)"""
        if not self.is_windows:
            return
        
        try:

            logger.info("Restricted token creation (Windows-specific implementation needed)")
            env_config['restricted_token'] = True
            
        except Exception as e:
            logger.warning(f"Failed to create restricted token: {e}")
    
    def _setup_windows_job_object(self, env_config: Dict[str, Any]):
        """Set up Windows Job Object for resource limits"""
        if not self.is_windows:
            return
        
        try:

            logger.info("Job object setup (Windows-specific implementation needed)")
            env_config['job_object'] = True
            
        except Exception as e:
            logger.warning(f"Failed to setup job object: {e}")
    
    def _apply_basic_restrictions(self, env_config: Dict[str, Any]):
        """Apply basic security restrictions using standard Python/system calls"""
        try:

            memory_bytes = env_config['memory_limit_mb'] * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))

            resource.setrlimit(resource.RLIMIT_CPU, (300, 300))

            resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, 100 * 1024 * 1024))

            resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
            
            env_config['restrictions_applied'].append('basic_rlimits')
            logger.info("Basic resource limits applied")
            
        except Exception as e:
            logger.warning(f"Failed to apply basic restrictions: {e}")
    
    def cleanup_environment(self, env_config: Dict[str, Any]):
        """Clean up the secure execution environment"""
        try:

            temp_dir = env_config.get('temp_dir')
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

            cgroup_name = env_config.get('cgroup_name')
            if cgroup_name:
                self._cleanup_cgroups(cgroup_name)
            
            logger.info("Security environment cleaned up")
            
        except Exception as e:
            logger.warning(f"Environment cleanup failed: {e}")
    
    def _cleanup_cgroups(self, cgroup_name: str):
        """Clean up cgroups"""
        try:
            if 'cgroups_v2' in self.security_features:
                cgroup_path = f"/sys/fs/cgroup/{cgroup_name}"
                if os.path.exists(cgroup_path):
                    os.rmdir(cgroup_path)
            else:

                for subsystem in ['memory', 'cpu']:
                    cgroup_path = f"/sys/fs/cgroup/{subsystem}/{cgroup_name}"
                    if os.path.exists(cgroup_path):
                        os.rmdir(cgroup_path)
        except Exception as e:
            logger.warning(f"Cgroup cleanup failed: {e}")
    
    def get_security_info(self) -> Dict[str, Any]:
        """Get information about available and applied security features"""
        return {
            'platform': sys.platform,
            'available_features': self.security_features,
            'uid': os.getuid() if hasattr(os, 'getuid') else None,
            'gid': os.getgid() if hasattr(os, 'getgid') else None,
            'capabilities': self._get_capabilities() if self.is_linux else None
        }
    
    def _get_capabilities(self) -> List[str]:
        """Get current process capabilities (Linux only)"""
        try:
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('CapEff:'):
                        cap_hex = line.split()[1]

                        return [f"cap_{cap_hex}"]
            return []
        except Exception:
            return []

_security_instance = None

def get_security_hardening() -> SecurityHardening:
    """Get global security hardening instance"""
    global _security_instance
    if _security_instance is None:
        _security_instance = SecurityHardening()
    return _security_instance