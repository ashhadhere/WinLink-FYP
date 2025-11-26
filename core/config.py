"""
Enhanced WinLink Configuration
Integrates all security and performance features
"""
import os
import logging
from typing import Dict, Any

SECURITY_CONFIG = {
    'enable_tls': True,
    'enable_authentication': True,
    'enable_containers': True,
    'enable_seccomp': True,
    'enable_apparmor': True,
    'enable_cgroups': True,

    'ssl_cert_file': 'ssl/server.crt',
    'ssl_key_file': 'ssl/server.key',
    'auth_token_file': 'secrets/auth_token.txt',

    'max_memory_mb': 512,
    'max_cpu_percent': 50,
    'max_execution_time': 300,
    'max_file_size_mb': 100,
    'max_processes': 10,

    'docker_image': 'winlink-task-executor:latest',
}

DATABASE_CONFIG = {
    'db_path': 'data/winlink.db',
    'enable_logging': True,
    'log_level': 'INFO',
    'cleanup_days': 30,

}

SCHEDULER_CONFIG = {
    'enable_advanced_scheduling': True,
    'enable_load_balancing': True,
    'default_priority': 'NORMAL',
    'scheduler_interval': 1.0,
    'max_retries': 3,
    'retry_delay_base': 5.0,

    'load_balancing_strategy': 'performance_based',  # round_robin, least_loaded, performance_based, capability_aware

    'default_max_concurrent_tasks': 5,
    'heartbeat_timeout': 300,
    'performance_window': 20,  # Number of recent tasks to consider for performance calculation
}

NETWORK_CONFIG = {
    'master_port': 9000,
    'worker_port': 9001,
    'heartbeat_interval': 30,
    'connection_timeout': 30,
    'tls_version': 'TLSv1.3',
    'cipher_suites': [
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
    ],
}

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
    'file_path': 'logs/winlink.log',
    'max_file_size_mb': 100,
    'backup_count': 5,
    'enable_console': True,
    'enable_file': True,
}

MONITORING_CONFIG = {
    'enable_resource_monitoring': True,
    'resource_collection_interval': 5,
    'enable_performance_metrics': True,
    'enable_security_logging': True,
    'health_check_interval': 60,
}

UI_CONFIG = {
    'enable_security_dashboard': True,
    'show_performance_metrics': True,
    'show_container_status': True,
    'refresh_interval_ms': 2000,
    'max_log_lines': 1000,
}

class WinLinkConfig:
    def __init__(self, config_file: str = None):
        self.config_file = config_file
        self.security = SECURITY_CONFIG.copy()
        self.database = DATABASE_CONFIG.copy()
        self.scheduler = SCHEDULER_CONFIG.copy()
        self.network = NETWORK_CONFIG.copy()
        self.logging = LOGGING_CONFIG.copy()
        self.monitoring = MONITORING_CONFIG.copy()
        self.ui = UI_CONFIG.copy()

        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

        self.apply_env_overrides()

        self._apply_config_overrides()
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        try:
            import json
            with open(config_file, 'r') as f:
                config_data = json.load(f)

            for section_name, section_config in config_data.items():
                if hasattr(self, section_name):
                    getattr(self, section_name).update(section_config)
                    
        except Exception as e:
            logging.error(f"Failed to load config from {config_file}: {e}")
    
    def apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mappings = {
            'WINLINK_TLS_ENABLED': ('security', 'enable_tls', bool),
            'WINLINK_AUTH_ENABLED': ('security', 'enable_authentication', bool),
            'WINLINK_CONTAINERS_ENABLED': ('security', 'enable_containers', bool),
            'WINLINK_MAX_MEMORY_MB': ('security', 'max_memory_mb', int),
            'WINLINK_MAX_CPU_PERCENT': ('security', 'max_cpu_percent', int),
            'WINLINK_DB_PATH': ('database', 'db_path', str),
            'WINLINK_LOG_LEVEL': ('logging', 'level', str),
            'WINLINK_MASTER_PORT': ('network', 'master_port', int),
            'WINLINK_WORKER_PORT': ('network', 'worker_port', int),
            'WINLINK_AUTH_TOKEN_FILE': ('security', 'auth_token_file', str),
            'WINLINK_SSL_CERT_FILE': ('security', 'ssl_cert_file', str),
            'WINLINK_SSL_KEY_FILE': ('security', 'ssl_key_file', str),
            'WINLINK_LOAD_BALANCING_STRATEGY': ('scheduler', 'load_balancing_strategy', str),
        }
        
        for env_var, (section, key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    if type_func == bool:
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        value = type_func(value)
                    getattr(self, section)[key] = value
                except (ValueError, TypeError) as e:
                    logging.warning(f"Invalid value for {env_var}: {value} ({e})")
    
    def _apply_config_overrides(self):
        """Apply configuration overrides from override file (e.g., minimal installation)"""
        override_file = 'config_override.py'
        if os.path.exists(override_file):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("config_override", override_file)
                override_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(override_module)

                if hasattr(override_module, 'DISABLE_CONTAINERS') and override_module.DISABLE_CONTAINERS:
                    self.security['enable_containers'] = False
                    logging.info("Containerization disabled by configuration override")
                
                if hasattr(override_module, 'CONTAINER_FALLBACK_ONLY') and override_module.CONTAINER_FALLBACK_ONLY:
                    self.security['enable_seccomp'] = False
                    self.security['enable_apparmor'] = False
                    logging.info("Container features disabled, using fallback execution only")
                    
            except Exception as e:
                logging.warning(f"Failed to load configuration overrides: {e}")
    
    def save_to_file(self, config_file: str):
        """Save current configuration to JSON file"""
        try:
            import json
            config_data = {
                'security': self.security,
                'database': self.database,
                'scheduler': self.scheduler,
                'network': self.network,
                'logging': self.logging,
                'monitoring': self.monitoring,
                'ui': self.ui,
            }
            
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to save config to {config_file}: {e}")
    
    def get_security_features(self) -> Dict[str, bool]:
        """Get enabled security features"""
        return {
            'TLS Encryption': self.security['enable_tls'],
            'Authentication': self.security['enable_authentication'],
            'Containerization': self.security['enable_containers'],
            'Seccomp Filtering': self.security['enable_seccomp'],
            'AppArmor Profile': self.security['enable_apparmor'],
            'Cgroups Limits': self.security['enable_cgroups'],
        }
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        valid = True

        if self.security['enable_tls']:
            cert_file = self.security['ssl_cert_file']
            key_file = self.security['ssl_key_file']
            if not os.path.exists(cert_file):
                logging.error(f"TLS enabled but certificate file not found: {cert_file}")
                valid = False
            if not os.path.exists(key_file):
                logging.error(f"TLS enabled but key file not found: {key_file}")
                valid = False
        
        if self.security['enable_authentication']:
            token_file = self.security['auth_token_file']
            if not os.path.exists(token_file):
                logging.error(f"Authentication enabled but token file not found: {token_file}")
                valid = False

        if self.security['max_memory_mb'] < 128:
            logging.warning(f"Memory limit very low: {self.security['max_memory_mb']}MB")
        
        if self.security['max_cpu_percent'] < 10:
            logging.warning(f"CPU limit very low: {self.security['max_cpu_percent']}%")

        if not (1024 <= self.network['master_port'] <= 65535):
            logging.error(f"Invalid master port: {self.network['master_port']}")
            valid = False
        
        if not (1024 <= self.network['worker_port'] <= 65535):
            logging.error(f"Invalid worker port: {self.network['worker_port']}")
            valid = False
        
        return valid
    
    def setup_logging(self):
        """Set up logging based on configuration"""
        log_level = getattr(logging, self.logging['level'].upper(), logging.INFO)

        log_file = self.logging['file_path']
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        handlers = []
        
        if self.logging['enable_console']:
            handlers.append(logging.StreamHandler())
        
        if self.logging['enable_file']:
            from logging.handlers import RotatingFileHandler
            max_bytes = self.logging['max_file_size_mb'] * 1024 * 1024
            handlers.append(RotatingFileHandler(
                log_file, 
                maxBytes=max_bytes,
                backupCount=self.logging['backup_count']
            ))

        logging.basicConfig(
            level=log_level,
            format=self.logging['format'],
            handlers=handlers,
            force=True
        )
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"WinLinkConfig(security_features={len([f for f in self.get_security_features().values() if f])})"

_config_instance = None

def get_config(config_file: str = None) -> WinLinkConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = WinLinkConfig(config_file)
    return _config_instance

def load_config(config_file: str = None) -> WinLinkConfig:
    """Load and return configuration"""
    config = get_config(config_file)
    config.setup_logging()
    
    if config.validate():
        logging.info("WinLink configuration loaded and validated successfully")
        enabled_features = [name for name, enabled in config.get_security_features().items() if enabled]
        logging.info(f"Security features enabled: {', '.join(enabled_features)}")
    else:
        logging.warning("Configuration validation failed - some features may not work correctly")
    
    return config

DEFAULT_CONFIG = WinLinkConfig()