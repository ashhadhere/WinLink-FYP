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
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.lock = threading.Lock()
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
    
    def connect_to_worker(self, worker_id: str, ip: str, port: int) -> bool:
        """Connect to a worker PC"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            
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
        except Exception as e:
            print(f"Failed to connect to worker {worker_id}: {e}")
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
    
    def stop(self):
        """Stop the network manager and disconnect all workers"""
        self.running = False
        worker_ids = list(self.workers.keys())
        for worker_id in worker_ids:
            self.disconnect_worker(worker_id)

class WorkerNetwork:
    def __init__(self):
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.message_handlers: Dict[str, Callable] = {}
        self.running = False
        self.ip = ""
        self.port = 0
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
    
    def start_server(self, port: int) -> bool:
        """Start server to accept connections from master"""
        try:
            self.ip = socket.gethostbyname(socket.gethostname())
            self.port = port
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, port))
            self.server_socket.listen(1)
            
            self.running = True
            
            # Start accepting connections
            threading.Thread(target=self._accept_connections, daemon=True).start()
            
            return True
        except Exception as e:
            print(f"Failed to start worker server: {e}")
            return False
    
    def _accept_connections(self):
        """Accept connections from master"""
        try:
            while self.running:
                self.client_socket, addr = self.server_socket.accept()
                print(f"Master connected from {addr}")
                
                # Send ready message
                ready_msg = NetworkMessage(MessageType.READY, {
                    'worker_id': f"{self.ip}:{self.port}",
                    'capabilities': ['computation', 'data_analysis']
                })
                self.client_socket.send(ready_msg.to_json().encode() + b'\n')
                
                # Start listening for messages
                threading.Thread(target=self._listen_to_master, daemon=True).start()
                
        except Exception as e:
            if self.running:
                print(f"Error accepting connections: {e}")
    
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
        print(f"[WORKER NETWORK] Received message type: {message.type}")
        if message.type in self.message_handlers:
            print(f"[WORKER NETWORK] Handler found for {message.type}, calling handler")
            self.message_handlers[message.type](message.data)
        elif message.type == MessageType.DISCONNECT:
            self.stop()
        else:
            print(f"[WORKER NETWORK] No handler for message type: {message.type}")
    
    def send_message_to_master(self, message: NetworkMessage) -> bool:
        """Send a message to the master"""
        if not self.client_socket:
            print(f"[WORKER NETWORK] ERROR: No client socket available to send {message.type}")
            return False
        
        try:
            json_data = message.to_json()
            print(f"[WORKER NETWORK] Sending {message.type} to master: {len(json_data)} bytes")
            self.client_socket.send(json_data.encode() + b'\n')
            print(f"[WORKER NETWORK] Message {message.type} sent successfully")
            return True
        except Exception as e:
            print(f"[WORKER NETWORK] ERROR sending message to master: {e}")
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
        print(f"[WORKER NETWORK] Preparing to send resource data: {list(resource_data.keys())}")
        msg = NetworkMessage(MessageType.RESOURCE_DATA, resource_data)
        result = self.send_message_to_master(msg)
        print(f"[WORKER NETWORK] Resource data sent: {result}")
        return result
    
    def stop(self):
        """Stop the worker network"""
        self.running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
