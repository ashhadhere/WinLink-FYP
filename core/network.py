"""
Network Protocol - Handles communication between Master and Worker PCs
"""
import json
import socket
import threading
import time
from typing import Dict, Any, Callable, Optional

class MessageType:
    # Master to Worker messages
    TASK_REQUEST = "task_request"
    RESOURCE_REQUEST = "resource_request"
    HEARTBEAT = "heartbeat"
    DISCONNECT = "disconnect"
    
    # Worker to Master messages
    TASK_RESULT = "task_result"
    RESOURCE_DATA = "resource_data"
    HEARTBEAT_RESPONSE = "heartbeat_response"
    READY = "ready"
    ERROR = "error"
    PROGRESS_UPDATE = "progress_update"
    
    # Discovery
    WORKER_DISCOVERY = "worker_discovery" 

class NetworkMessage:
    def __init__(self, msg_type: str, data: Dict[str, Any] = None):
        self.type = msg_type
        self.data = data or {}
        self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps({
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        try:
            data = json.loads(json_str)
            msg = cls(data['type'], data.get('data', {}))
            msg.timestamp = data.get('timestamp', time.time())
            return msg
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid message format: {e}")

class MasterNetwork:
    def __init__(self):
        self.workers: Dict[str, socket.socket] = {}
        self.worker_info: Dict[str, Dict] = {}
        self.discovered_workers: Dict[str, Dict] = {}  # Workers found via UDP broadcast
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.lock = threading.Lock()
        self.discovery_socket: Optional[socket.socket] = None
        self.discovery_port = 5000  # Port for UDP discovery
    def broadcast_task(self, task_id: str, code: str, data: Dict[str, Any]):
        """Send the task to all connected workers"""
        task_data = {
            'task_id': task_id,
            'code': code,
            'data': data
        }
        for worker_id in list(self.workers.keys()):
            self.send_task_to_worker(worker_id, task_data)

    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    def connect_to_worker(self, worker_id: str, ip: str, port: int, retries: int = 3) -> bool:
        """Connect to a worker PC with retry logic"""
        print(f"\n[MASTER] ========== CONNECTION ATTEMPT ==========")
        print(f"[MASTER] Target: {worker_id}")
        print(f"[MASTER] Will attempt {retries} times with 3-second delays")
        
        for attempt in range(retries):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10.0)  # Increased to 10 seconds
                
                # Enable TCP keepalive
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # Set TCP_NODELAY for low latency
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                if attempt > 0:
                    print(f"[MASTER] ⏳ Retry {attempt}/{retries-1}: Attempting connection...")
                else:
                    print(f"[MASTER] 🔄 Attempt 1/{retries}: Connecting to {ip}:{port}...")
                
                # Try to connect
                sock.connect((ip, port))
                sock.settimeout(30.0)  # 30 second timeout for operations after connection
                print(f"[MASTER] ✅ Successfully connected to {worker_id}")
                print(f"[MASTER] ============================================\n")
                
                with self.lock:
                    self.workers[worker_id] = sock
                    self.worker_info[worker_id] = {
                        'ip': ip,
                        'port': port,
                        'connected_at': time.time(),
                        'last_heartbeat': time.time(),
                        'status': 'connected'
                    }
                
                # Start listening for messages from this worker
                threading.Thread(
                    target=self._listen_to_worker,
                    args=(worker_id, sock),
                    daemon=True
                ).start()
                
                return True
                
            except socket.timeout:
                print(f"[MASTER] ⏱️  Connection timed out (waited 10 seconds)")
                if attempt < retries - 1:
                    print(f"[MASTER] 💤 Waiting 3 seconds before retry...")
                    time.sleep(3)
                    continue
                print(f"\n[MASTER] ❌ Connection failed after {retries} attempts")
                print(f"[MASTER] Possible causes:")
                print(f"[MASTER]   1. Worker is not running or didn't click 'Start Worker'")
                print(f"[MASTER]   2. **FIREWALL is blocking the connection** (most common!)")
                print(f"[MASTER]   3. Wrong IP address: {ip}")
                print(f"[MASTER]   4. Wrong port: {port}")
                print(f"[MASTER]   5. Different network (check both PCs are on same WiFi/LAN)")
                print(f"[MASTER] ")
                print(f"[MASTER] 🛡️  FIREWALL FIX (Run as Administrator on BOTH PCs):")
                print(f"[MASTER]   netsh advfirewall firewall add rule name=\"WinLink\" dir=in action=allow protocol=TCP localport={port} enable=yes")
                print(f"[MASTER] ============================================\n")
                return False
                
            except ConnectionRefusedError:
                print(f"[MASTER] 🚫 Connection refused")
                if attempt < retries - 1:
                    print(f"[MASTER] 💤 Worker may still be starting, waiting 3 seconds...")
                    time.sleep(3)
                    continue
                print(f"\n[MASTER] ❌ Connection refused after {retries} attempts")
                print(f"[MASTER] This means Worker is NOT listening on {ip}:{port}")
                print(f"[MASTER] Solutions:")
                print(f"[MASTER]   1. Check Worker console shows: '✅ Server started successfully'")
                print(f"[MASTER]   2. Verify Worker clicked 'Start Worker' button")
                print(f"[MASTER]   3. Check port number matches (Worker shows IP:PORT)")
                print(f"[MASTER] ============================================\n")
                return False
                
            except OSError as e:
                if e.errno == 10061:  # Connection refused (Windows)
                    if attempt < retries - 1:
                        print(f"[MASTER] ⏳ Worker not ready, waiting 3 seconds...")
                        time.sleep(3)
                        continue
                elif e.errno == 10065:  # No route to host
                    print(f"[MASTER] 🌐 No route to host {ip}")
                    print(f"[MASTER] Check both PCs are on the same network")
                    return False
                print(f"[MASTER] ❌ Network error: {e}")
                print(f"[MASTER] ============================================\n")
                return False
                
            except Exception as e:
                if attempt < retries - 1:
                    print(f"[MASTER] ⚠️  Error: {e}")
                    print(f"[MASTER] 💤 Waiting 3 seconds before retry...")
                    time.sleep(3)
                    continue
                print(f"\n[MASTER] ❌ Failed to connect: {e}")
                print(f"[MASTER] ============================================\n")
                return False
        
        return False
    
    def disconnect_worker(self, worker_id: str):
        """Disconnect from a worker"""
        with self.lock:
            if worker_id in self.workers:
                try:
                    # Send disconnect message
                    msg = NetworkMessage(MessageType.DISCONNECT)
                    self.workers[worker_id].send(msg.to_json().encode() + b'\n')
                    self.workers[worker_id].close()
                except:
                    pass
                
                del self.workers[worker_id]
                if worker_id in self.worker_info:
                    self.worker_info[worker_id]['status'] = 'disconnected'
    
    def send_task_to_worker(self, worker_id: str, task_data: Dict) -> bool:
        """Send a task to a specific worker"""
        msg = NetworkMessage(MessageType.TASK_REQUEST, task_data)
        return self._send_message_to_worker(worker_id, msg)
    
    def request_resources_from_worker(self, worker_id: str) -> bool:
        """Request system resource data from a worker"""
        print(f"[NETWORK] Requesting resources from {worker_id}")
        msg = NetworkMessage(MessageType.RESOURCE_REQUEST, {})
        result = self._send_message_to_worker(worker_id, msg)
        print(f"[NETWORK] Resource request sent to {worker_id}: {result}")
        return result
    
    def _send_message_to_worker(self, worker_id: str, message: NetworkMessage) -> bool:
        """Send a message to a worker"""
        with self.lock:
            if worker_id not in self.workers:
                return False
            
            try:
                sock = self.workers[worker_id]
                sock.send(message.to_json().encode() + b'\n')
                return True
            except Exception as e:
                print(f"Failed to send message to worker {worker_id}: {e}")
                # Remove disconnected worker
                self._remove_worker(worker_id)
                return False
    
    def _listen_to_worker(self, worker_id: str, sock: socket.socket):
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
                            message = NetworkMessage.from_json(line.strip())
                            self._handle_worker_message(worker_id, message)
                        except Exception as e:
                            print(f"Error processing message from {worker_id}: {e}")
        
        except Exception as e:
            print(f"Connection lost with worker {worker_id}: {e}")
        finally:
            self._remove_worker(worker_id)
    
    def _handle_worker_message(self, worker_id: str, message: NetworkMessage):
        """Handle a message from a worker"""
        print(f"[MASTER NETWORK] Received message from {worker_id}, type: {message.type}")
        
        # Update last heartbeat
        with self.lock:
            if worker_id in self.worker_info:
                self.worker_info[worker_id]['last_heartbeat'] = time.time()
        
        # Call registered handler
        if message.type in self.message_handlers:
            print(f"[MASTER NETWORK] Calling handler for {message.type}")
            self.message_handlers[message.type](worker_id, message.data)
        else:
            print(f"[MASTER NETWORK] No handler registered for {message.type}")
    
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
    
    def get_connected_workers(self) -> Dict[str, Dict]:
        """Get information about connected workers"""
        with self.lock:
            return {wid: info.copy() for wid, info in self.worker_info.items() 
                   if info['status'] == 'connected'}
    
    def start(self):
        """Start the network manager"""
        self.running = True
        self._start_discovery_listener()
    
    def _start_discovery_listener(self):
        """Start UDP listener for worker discovery broadcasts"""
        def listen():
            try:
                self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.discovery_socket.bind(('', self.discovery_port))
                self.discovery_socket.settimeout(1.0)
                
                print(f"[MASTER] Discovery listener started on port {self.discovery_port}")
                
                while self.running:
                    try:
                        data, addr = self.discovery_socket.recvfrom(1024)
                        message = json.loads(data.decode())
                        
                        if message.get('type') == MessageType.WORKER_DISCOVERY:
                            worker_data = message.get('data', {})
                            worker_id = f"{worker_data.get('ip')}:{worker_data.get('port')}"
                            
                            with self.lock:
                                self.discovered_workers[worker_id] = {
                                    'hostname': worker_data.get('hostname'),
                                    'ip': worker_data.get('ip'),
                                    'port': worker_data.get('port'),
                                    'last_seen': time.time()
                                }
                            print(f"[MASTER] Discovered worker: {worker_id} ({worker_data.get('hostname')})")
                    
                    except socket.timeout:
                        # Clean up stale workers (not seen in last 15 seconds)
                        with self.lock:
                            current_time = time.time()
                            stale = [wid for wid, info in self.discovered_workers.items()
                                   if current_time - info.get('last_seen', 0) > 15]
                            for wid in stale:
                                self.discovered_workers.pop(wid, None)
                        continue
                    except Exception as e:
                        if self.running:
                            print(f"[MASTER] Error in discovery listener: {e}")
            
            except Exception as e:
                print(f"[MASTER] Failed to start discovery listener: {e}")
        
        threading.Thread(target=listen, daemon=True).start()
    
    def get_discovered_workers(self) -> Dict[str, Dict]:
        """Get list of discovered workers"""
        with self.lock:
            return self.discovered_workers.copy()
    
    def stop(self):
        """Stop the network manager and disconnect all workers"""
        self.running = False
        if self.discovery_socket:
            try:
                self.discovery_socket.close()
            except:
                pass
        worker_ids = list(self.workers.keys())
        for worker_id in worker_ids:
            self.disconnect_worker(worker_id)

class WorkerNetwork:
    def __init__(self):
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.broadcast_socket: Optional[socket.socket] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.connection_callback: Optional[Callable] = None  # Callback when master connects
        self.running = False
        self.broadcasting = False
        self.ip = ""
        self.port = 0
        self.hostname = socket.gethostname()
        self.discovery_port = 5000
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    def set_connection_callback(self, callback: Callable):
        """Set callback to be called when master connects"""
        self.connection_callback = callback
    
    def start_server(self, port: int) -> bool:
        """Start server to accept connections from master"""
        max_retries = 3
        for retry in range(max_retries):
            try:
                self.ip = socket.gethostbyname(socket.gethostname())
                self.port = port
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Windows-specific socket options for better port reuse
                try:
                    # SO_EXCLUSIVEADDRUSE = 0 allows immediate port reuse
                    self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 0)
                except (AttributeError, OSError):
                    pass  # Not on Windows or not supported
                
                # Set socket to non-blocking for better control
                self.server_socket.settimeout(1.0)
                
                print(f"[WORKER] Binding to {self.ip}:{port} (attempt {retry + 1}/{max_retries})")
                self.server_socket.bind(('0.0.0.0', port))  # Listen on all interfaces
                self.server_socket.listen(10)  # Allow up to 10 pending connections
                
                # Verify we can actually accept connections
                print(f"[WORKER] ✅ Server started successfully on {self.ip}:{port}")
                print(f"[WORKER] 🌐 Listening on all network interfaces (0.0.0.0:{port})")
                print(f"[WORKER] 📡 Master should connect to: {self.ip}:{port}")
                print(f"[WORKER] ")
                print(f"[WORKER] 🛡️  IMPORTANT - Firewall Configuration:")
                print(f"[WORKER]   If Master cannot connect, run this as Administrator:")
                print(f"[WORKER]   netsh advfirewall firewall add rule name=\"WinLink\" dir=in action=allow protocol=TCP localport={port} enable=yes")
                print(f"[WORKER] ")
                print(f"[WORKER] Ready to accept connections from Master PC")
                
                self.running = True
                
                # Start accepting connections
                threading.Thread(target=self._accept_connections, daemon=True).start()
                
                # Start broadcasting presence
                self._start_broadcast()
                
                return True
                
            except OSError as e:
                if e.errno == 10048 or e.errno == 48:  # Address already in use (Windows/Unix)
                    if retry < max_retries - 1:
                        print(f"[WORKER] Port {port} is in use, waiting 3 seconds for release...")
                        time.sleep(3)
                        continue
                    print(f"[WORKER] ❌ Port {port} is still in use after {max_retries} attempts.")
                    print(f"[WORKER] Solution: Run 'restart_clean.bat' or use a different port.")
                    return False
                elif e.errno == 10049:  # Cannot assign requested address
                    print(f"[WORKER] ❌ Cannot bind to {self.ip}:{port} - invalid address")
                    return False
                else:
                    print(f"[WORKER] ❌ Socket error: {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False
                    
            except Exception as e:
                print(f"[WORKER] ❌ Failed to start worker server: {e}")
                if retry < max_retries - 1:
                    time.sleep(2)
                    continue
                return False
        
        return False
    
    def _start_broadcast(self):
        """Start broadcasting worker presence via UDP"""
        def broadcast():
            try:
                self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.broadcasting = True
                
                discovery_message = {
                    'type': MessageType.WORKER_DISCOVERY,
                    'data': {
                        'hostname': self.hostname,
                        'ip': self.ip,
                        'port': self.port
                    }
                }
                
                print(f"[WORKER] Starting broadcast: {self.hostname} at {self.ip}:{self.port}")
                
                while self.broadcasting and self.running:
                    try:
                        message_json = json.dumps(discovery_message)
                        self.broadcast_socket.sendto(
                            message_json.encode(),
                            ('<broadcast>', self.discovery_port)
                        )
                        time.sleep(3)  # Broadcast every 3 seconds
                    except Exception as e:
                        if self.broadcasting:
                            print(f"[WORKER] Broadcast error: {e}")
                        break
            
            except Exception as e:
                print(f"[WORKER] Failed to start broadcast: {e}")
        
        threading.Thread(target=broadcast, daemon=True).start()
    
    def _accept_connections(self):
        """Accept connections from master"""
        print(f"[WORKER] Listening for Master connections...")
        try:
            while self.running:
                try:
                    self.client_socket, addr = self.server_socket.accept()
                    
                    # Configure client socket
                    self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    self.client_socket.settimeout(30.0)  # 30 second timeout for operations
                    
                    print(f"[WORKER] ✅ Master connected from {addr[0]}:{addr[1]}")
                    
                    # Call connection callback if set
                    if self.connection_callback:
                        self.connection_callback(addr)
                    
                    # Send ready message
                    ready_msg = NetworkMessage(MessageType.READY, {
                        'worker_id': f"{self.ip}:{self.port}",
                        'capabilities': ['computation', 'data_analysis']
                    })
                    self.client_socket.send(ready_msg.to_json().encode() + b'\n')
                    
                    # Start listening for messages
                    threading.Thread(target=self._listen_to_master, daemon=True).start()
                    
                except socket.timeout:
                    # Timeout on accept() is normal, allows checking self.running
                    continue
                except Exception as e:
                    if self.running:
                        print(f"[WORKER] Error accepting connection: {e}")
                        time.sleep(1)  # Brief pause before retrying
                
        except Exception as e:
            if self.running:
                print(f"[WORKER] Fatal error in accept loop: {e}")
    
    def _listen_to_master(self):
        """Listen for messages from master"""
        buffer = ""
        try:
            while self.running and self.client_socket:
                data = self.client_socket.recv(4096).decode()
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = NetworkMessage.from_json(line.strip())
                            self._handle_master_message(message)
                        except Exception as e:
                            print(f"Error processing message from master: {e}")
        
        except Exception as e:
            print(f"Connection lost with master: {e}")
        finally:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
    
    def _handle_master_message(self, message: NetworkMessage):
        """Handle a message from master"""
        if message.type in self.message_handlers:
            self.message_handlers[message.type](message.data)
        elif message.type == MessageType.DISCONNECT:
            self.stop()
    
    def send_message_to_master(self, message: NetworkMessage) -> bool:
        """Send a message to the master"""
        if not self.client_socket:
            return False
        
        try:
            json_data = message.to_json()
            self.client_socket.send(json_data.encode() + b'\n')
            return True
        except Exception as e:
            return False
    
    def send_task_result(self, task_id: str, result_data: Dict) -> bool:
        """Send task result to master"""
        msg = NetworkMessage(MessageType.TASK_RESULT, {
            'task_id': task_id,
            'result': result_data
        })
        return self.send_message_to_master(msg)
    
    def send_resource_data(self, resource_data: Dict) -> bool:
        """Send system resource data to master"""
        msg = NetworkMessage(MessageType.RESOURCE_DATA, resource_data)
        return self.send_message_to_master(msg)
    
    def stop(self):
        """Stop the worker network"""
        print("[WORKER] Stopping network...")
        self.running = False
        self.broadcasting = False
        
        # Stop broadcast socket
        if self.broadcast_socket:
            try:
                self.broadcast_socket.close()
            except:
                pass
            self.broadcast_socket = None
        
        # Stop client connection
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        
        # Stop server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
        
        # Give the OS time to release the port
        time.sleep(0.5)
        print("[WORKER] Network stopped")
