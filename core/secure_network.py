"""
Secure Network Protocol with TLS encryption and token authentication
Enhanced version of the original network.py with security features
"""
import json
import socket
import ssl
import threading
import time
import logging
import hmac
import hashlib
import secrets
import os
from typing import Dict, Any, Callable, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class MessageType:
    # Master to Worker messages
    TASK_REQUEST = "task_request"
    RESOURCE_REQUEST = "resource_request"
    HEARTBEAT = "heartbeat"
    DISCONNECT = "disconnect"
    AUTH_CHALLENGE = "auth_challenge"
    
    # Worker to Master messages
    TASK_RESULT = "task_result"
    RESOURCE_DATA = "resource_data"
    HEARTBEAT_RESPONSE = "heartbeat_response"
    READY = "ready"
    ERROR = "error"
    PROGRESS_UPDATE = "progress_update"
    AUTH_RESPONSE = "auth_response"

class SecureNetworkMessage:
    def __init__(self, msg_type: str, data: Dict[str, Any] = None, encrypted=False):
        self.type = msg_type
        self.data = data or {}
        self.timestamp = time.time()
        self.encrypted = encrypted
    
    def to_json(self) -> str:
        return json.dumps({
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp,
            'encrypted': self.encrypted
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        try:
            data = json.loads(json_str)
            msg = cls(data['type'], data.get('data', {}), data.get('encrypted', False))
            msg.timestamp = data.get('timestamp', time.time())
            return msg
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid message format: {e}")

class AuthenticationManager:
    def __init__(self, auth_token_file: str = None):
        self.auth_token_file = auth_token_file or "secrets/auth_token.txt"
        self.session_tokens: Dict[str, Dict] = {}
        self.token_expiry = 3600  # 1 hour
        self._load_auth_token()
    
    def _load_auth_token(self):
        """Load authentication token from file"""
        try:
            if os.path.exists(self.auth_token_file):
                with open(self.auth_token_file, 'r') as f:
                    self.master_token = f.read().strip()
            else:
                # Generate new token
                self.master_token = self._generate_token()
                os.makedirs(os.path.dirname(self.auth_token_file), exist_ok=True)
                with open(self.auth_token_file, 'w') as f:
                    f.write(self.master_token)
                os.chmod(self.auth_token_file, 0o600)  # Restrict access
                
            logger.info(f"Authentication token loaded/generated: {self.auth_token_file}")
        except Exception as e:
            logger.error(f"Failed to load auth token: {e}")
            self.master_token = self._generate_token()
    
    def _generate_token(self) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    def create_challenge(self, client_id: str) -> str:
        """Create authentication challenge for client"""
        challenge = secrets.token_urlsafe(16)
        self.session_tokens[client_id] = {
            'challenge': challenge,
            'created_at': time.time(),
            'authenticated': False
        }
        return challenge
    
    def verify_response(self, client_id: str, response: str) -> bool:
        """Verify client's authentication response"""
        if client_id not in self.session_tokens:
            return False
        
        session = self.session_tokens[client_id]
        
        # Check if challenge is still valid (not expired)
        if time.time() - session['created_at'] > 300:  # 5 minutes
            del self.session_tokens[client_id]
            return False
        
        # Expected response: HMAC(token, challenge)
        expected_response = hmac.new(
            self.master_token.encode(),
            session['challenge'].encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(expected_response, response):
            session['authenticated'] = True
            session['auth_time'] = time.time()
            return True
        
        return False
    
    def is_authenticated(self, client_id: str) -> bool:
        """Check if client is authenticated"""
        if client_id not in self.session_tokens:
            return False
        
        session = self.session_tokens[client_id]
        if not session.get('authenticated', False):
            return False
        
        # Check token expiry
        if time.time() - session.get('auth_time', 0) > self.token_expiry:
            del self.session_tokens[client_id]
            return False
        
        return True

class TLSSocketWrapper:
    """Wrapper for TLS-enabled socket communication"""
    
    def __init__(self, cert_file: str = None, key_file: str = None, ca_file: str = None):
        self.cert_file = cert_file or "ssl/server.crt"
        self.key_file = key_file or "ssl/server.key"
        self.ca_file = ca_file or "ssl/ca.crt"
        self._ensure_ssl_certs()
    
    def _ensure_ssl_certs(self):
        """Ensure SSL certificates exist, generate self-signed if needed"""
        ssl_dir = os.path.dirname(self.cert_file)
        if not os.path.exists(ssl_dir):
            os.makedirs(ssl_dir, exist_ok=True)
        
        if not all(os.path.exists(f) for f in [self.cert_file, self.key_file]):
            logger.warning("SSL certificates not found, generating self-signed certificates...")
            self._generate_self_signed_cert()
    
    def _generate_self_signed_cert(self):
        """Generate self-signed SSL certificate for testing"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "WinLink"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    x509.IPAddress(ipaddress.IPv6Address("::1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Write private key
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Set file permissions
            os.chmod(self.key_file, 0o600)
            os.chmod(self.cert_file, 0o644)
            
            logger.info(f"Generated self-signed certificate: {self.cert_file}")
            
        except Exception as e:
            logger.error(f"Failed to generate SSL certificate: {e}")
            # Create dummy files to prevent repeated attempts
            with open(self.cert_file, 'w') as f:
                f.write("# Dummy certificate file\n")
            with open(self.key_file, 'w') as f:
                f.write("# Dummy key file\n")
    
    def create_server_context(self) -> ssl.SSLContext:
        """Create SSL context for server"""
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        try:
            context.load_cert_chain(self.cert_file, self.key_file)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE  # For self-signed certs
            return context
        except Exception as e:
            logger.warning(f"Failed to create server SSL context: {e}")
            return None
    
    def create_client_context(self) -> ssl.SSLContext:
        """Create SSL context for client"""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # For self-signed certs
        return context

class SecureMasterNetwork:
    def __init__(self, use_tls=True, auth_token_file=None):
        self.workers: Dict[str, ssl.SSLSocket] = {}
        self.worker_info: Dict[str, Dict] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.lock = threading.Lock()
        
        # Security components
        self.use_tls = use_tls
        self.auth_manager = AuthenticationManager(auth_token_file)
        self.tls_wrapper = TLSSocketWrapper() if use_tls else None
        
        logger.info(f"Secure Master Network initialized (TLS: {use_tls})")
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    def connect_to_worker(self, worker_id: str, ip: str, port: int) -> bool:
        """Connect to a worker PC with TLS and authentication"""
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Wrap with TLS if enabled
            if self.use_tls and self.tls_wrapper:
                context = self.tls_wrapper.create_client_context()
                if context:
                    sock = context.wrap_socket(sock, server_hostname=ip)
            
            sock.connect((ip, port))
            
            # Perform authentication handshake
            if not self._authenticate_worker(sock, worker_id):
                sock.close()
                return False
            
            with self.lock:
                self.workers[worker_id] = sock
                self.worker_info[worker_id] = {
                    'ip': ip,
                    'port': port,
                    'connected_at': time.time(),
                    'last_heartbeat': time.time(),
                    'status': 'connected',
                    'authenticated': True
                }
            
            # Start listening for messages from this worker
            threading.Thread(
                target=self._listen_to_worker,
                args=(worker_id, sock),
                daemon=True
            ).start()
            
            logger.info(f"Securely connected to worker {worker_id} at {ip}:{port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to worker {worker_id}: {e}")
            return False
    
    def _authenticate_worker(self, sock: socket.socket, worker_id: str) -> bool:
        """Perform authentication handshake with worker"""
        try:
            # Send authentication challenge
            challenge = self.auth_manager.create_challenge(worker_id)
            challenge_msg = SecureNetworkMessage(MessageType.AUTH_CHALLENGE, {
                'challenge': challenge
            })
            sock.send(challenge_msg.to_json().encode() + b'\n')
            
            # Wait for response
            response_data = sock.recv(4096).decode().strip()
            response_msg = SecureNetworkMessage.from_json(response_data)
            
            if response_msg.type != MessageType.AUTH_RESPONSE:
                logger.warning(f"Worker {worker_id} sent invalid auth response type")
                return False
            
            # Verify response
            auth_response = response_msg.data.get('response', '')
            if self.auth_manager.verify_response(worker_id, auth_response):
                logger.info(f"Worker {worker_id} authenticated successfully")
                return True
            else:
                logger.warning(f"Worker {worker_id} authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed for worker {worker_id}: {e}")
            return False
    
    def _send_message_to_worker(self, worker_id: str, message: SecureNetworkMessage) -> bool:
        """Send a secure message to a worker"""
        with self.lock:
            if worker_id not in self.workers:
                return False
            
            if not self.auth_manager.is_authenticated(worker_id):
                logger.warning(f"Worker {worker_id} not authenticated, rejecting message")
                return False
            
            try:
                sock = self.workers[worker_id]
                sock.send(message.to_json().encode() + b'\n')
                return True
            except Exception as e:
                logger.error(f"Failed to send message to worker {worker_id}: {e}")
                self._remove_worker(worker_id)
                return False
    
    def send_task_to_worker(self, worker_id: str, task_data: Dict) -> bool:
        """Send a task to a specific worker"""
        msg = SecureNetworkMessage(MessageType.TASK_REQUEST, task_data)
        return self._send_message_to_worker(worker_id, msg)
    
    def request_resources_from_worker(self, worker_id: str) -> bool:
        """Request system resource data from a worker"""
        msg = SecureNetworkMessage(MessageType.RESOURCE_REQUEST, {})
        return self._send_message_to_worker(worker_id, msg)
    
    # ... (rest of the methods remain similar to original, with TLS and auth checks)
    
    def _listen_to_worker(self, worker_id: str, sock):
        """Listen for messages from a worker"""
        buffer = ""
        try:
            while self.running and worker_id in self.workers:
                data = sock.recv(4096).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = SecureNetworkMessage.from_json(line.strip())
                            if self.auth_manager.is_authenticated(worker_id):
                                self._handle_worker_message(worker_id, message)
                            else:
                                logger.warning(f"Message from unauthenticated worker {worker_id}")
                        except Exception as e:
                            logger.error(f"Error processing message from {worker_id}: {e}")
        
        except Exception as e:
            logger.error(f"Connection lost with worker {worker_id}: {e}")
        finally:
            self._remove_worker(worker_id)
    
    def _handle_worker_message(self, worker_id: str, message: SecureNetworkMessage):
        """Handle a message from a worker"""
        # Update last heartbeat
        with self.lock:
            if worker_id in self.worker_info:
                self.worker_info[worker_id]['last_heartbeat'] = time.time()
        
        # Call registered handler
        if message.type in self.message_handlers:
            self.message_handlers[message.type](worker_id, message.data)
    
    def _remove_worker(self, worker_id: str):
        """Remove a worker from active connections"""
        with self.lock:
            if worker_id in self.workers:
                try:
                    self.workers[worker_id].close()
                except:
                    pass
                del self.workers[worker_id]
            
            if worker_id in self.worker_info:
                self.worker_info[worker_id]['status'] = 'disconnected'
        
        # Clean up authentication session
        if worker_id in self.auth_manager.session_tokens:
            del self.auth_manager.session_tokens[worker_id]
    
    def get_connected_workers(self) -> Dict[str, Dict]:
        """Get information about connected workers"""
        with self.lock:
            return {wid: info.copy() for wid, info in self.worker_info.items() 
                   if info['status'] == 'connected'}
    
    def start(self):
        """Start the network manager"""
        self.running = True
    
    def stop(self):
        """Stop the network manager and disconnect all workers"""
        self.running = False
        worker_ids = list(self.workers.keys())
        for worker_id in worker_ids:
            self.disconnect_worker(worker_id)
    
    def disconnect_worker(self, worker_id: str):
        """Disconnect from a worker"""
        with self.lock:
            if worker_id in self.workers:
                try:
                    msg = SecureNetworkMessage(MessageType.DISCONNECT)
                    self.workers[worker_id].send(msg.to_json().encode() + b'\n')
                    self.workers[worker_id].close()
                except:
                    pass
                
                del self.workers[worker_id]
                if worker_id in self.worker_info:
                    self.worker_info[worker_id]['status'] = 'disconnected'

# Secure Worker Network implementation would be similar...
# For brevity, I'm showing the pattern. The full implementation would include:
# - SecureWorkerNetwork class with TLS client functionality
# - Authentication response handling
# - Message encryption/decryption if needed

# Backward compatibility aliases
MasterNetwork = SecureMasterNetwork