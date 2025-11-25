"""
Task Manager - Handles task distribution and execution
"""
import json
import time
import uuid
import threading
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

class TaskType(Enum):
    CUSTOM = "custom"  # ✅ Add this line
    COMPUTATION = "computation"
    FILE_PROCESSING = "file_processing"
    IMAGE_PROCESSING = "image_processing"
    DATA_ANALYSIS = "data_analysis"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    type: TaskType
    code: str
    data: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    worker_id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: int = 0
    output: Optional[str] = None  # Full output including stdout/stderr
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'code': self.code,
            'data': self.data,
            'status': self.status.value,
            'worker_id': self.worker_id,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'progress': self.progress  # <-- NEW
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(
            id=data['id'],
            type=TaskType(data['type']),
            code=data['code'],
            data=data['data'],
            status=TaskStatus(data['status']),
            worker_id=data.get('worker_id'),
            result=data.get('result'),
            error=data.get('error'),
            created_at=data.get('created_at'),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at')
        )
        return task

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.lock = threading.Lock()
    
    # ── Task lifecycle helpers ──
    
    def create_task(self, task_type: TaskType, code: str, data: Dict[str, Any]) -> str:
        """Create a new task and add it to the queue"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            type=task_type,
            code=code,
            data=data
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_queue.append(task_id)
        
        return task_id
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task from the queue"""
        with self.lock:
            for task_id in self.task_queue:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.RUNNING
                    task.started_at = time.time()
                    return task
        return None
    
    def complete_task(self, task_id: str, result: Any = None, error: str = None):
        """Mark a task as completed or failed"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.completed_at = time.time()
                if error:
                    task.status = TaskStatus.FAILED
                    task.error = error
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
    
    def assign_task_to_worker(self, task_id: str, worker_id: str):
        """Assign a task to a specific worker"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].worker_id = worker_id
                if self.tasks[task_id].status == TaskStatus.PENDING:
                    self.tasks[task_id].status = TaskStatus.RUNNING
                    self.tasks[task_id].started_at = time.time()
    
    def update_task(self, task_id: str, worker_id: str, result_payload: Dict[str, Any]):
        """Update a task with result information from a worker"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            
            task.worker_id = worker_id
            task.completed_at = time.time()
            success = result_payload.get('success', True)
            task.result = result_payload.get('result')
            task.error = result_payload.get('error')
            task.progress = 100 if success else task.progress
            task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            
            # Store full output
            output_parts = []
            if result_payload.get('stdout'):
                output_parts.append(f"STDOUT:\n{result_payload['stdout']}")
            if result_payload.get('stderr'):
                output_parts.append(f"STDERR:\n{result_payload['stderr']}")
            if result_payload.get('result') is not None:
                result_val = result_payload.get('result')
                if isinstance(result_val, dict):
                    output_parts.append(f"RESULT:\n{json.dumps(result_val, indent=2)}")
                else:
                    output_parts.append(f"RESULT:\n{result_val}")
            if result_payload.get('error'):
                output_parts.append(f"ERROR:\n{result_payload['error']}")
            
            task.output = "\n\n".join(output_parts) if output_parts else None
    
    def update_task_progress(self, task_id: str, progress: int):
        """Update progress for a specific task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
            task.progress = max(0, min(100, int(progress)))
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get tasks by their status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def clear_tasks(self, status: Optional[TaskStatus] = None):
        """Remove tasks entirely or by status"""
        with self.lock:
            if status is None:
                self.tasks.clear()
                self.task_queue.clear()
                return
            
            to_remove = [task_id for task_id, task in self.tasks.items() if task.status == status]
            for task_id in to_remove:
                self.tasks.pop(task_id, None)
                if task_id in self.task_queue:
                    self.task_queue.remove(task_id)

# Predefined task templates
TASK_TEMPLATES = {
    "hello_world": {
        "type": TaskType.COMPUTATION,
        "name": "Hello World Test",
        "description": "Simple test task to verify output display",
        "code": """
# This is a simple test task
print("Hello from Worker!")
print("Task is executing...")

# Get the name from data
name = data.get('name', 'World')
message = f"Hello, {name}!"

print(f"Generated message: {message}")

# Set the result
result = {
    'message': message,
    'length': len(message),
    'uppercase': message.upper(),
    'status': 'success'
}

print("Task completed successfully!")
""",
        "sample_data": {"name": "WinLink User"}
    },
    
    "fibonacci": {
        "type": TaskType.COMPUTATION,
        "name": "Fibonacci Series",
        "description": "Generate Fibonacci series up to n terms and calculate the nth number",
        "code": """
def fibonacci_series(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    series = [0, 1]
    for i in range(2, n):
        series.append(series[i-1] + series[i-2])
    return series

def fibonacci_nth(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

n = data.get('n', 10)
series = fibonacci_series(n)
nth_value = fibonacci_nth(n)

result = {
    'series': series,
    'nth_number': nth_value,
    'count': len(series),
    'sum': sum(series)
}
""",
        "sample_data": {"n": 10}
    },
    
    "prime_check": {
        "type": TaskType.COMPUTATION,
        "name": "Prime Number Check",
        "description": "Check if a number is prime",
        "code": """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

result = is_prime(data['number'])
""",
        "sample_data": {"number": 982451653}
    },
    
    "factorial": {
        "type": TaskType.COMPUTATION,
        "name": "Factorial Calculation",
        "description": "Calculate factorial of a number n (n!)",
        "code": """
def factorial(n):
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

n = data.get('n', 10)
fact = factorial(n)

result = {
    'number': n,
    'factorial': fact,
    'formula': f"{n}!"
}
""",
        "sample_data": {"n": 10}
    },
    
    "matrix_multiply": {
        "type": TaskType.COMPUTATION,
        "name": "Matrix Multiplication",
        "description": "Multiply two matrices",
        "code": """
def matrix_multiply(A, B):
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    
    if cols_A != rows_B:
        raise ValueError("Cannot multiply matrices")
    
    result = [[0 for _ in range(cols_B)] for _ in range(rows_A)]
    
    for i in range(rows_A):
        for j in range(cols_B):
            for k in range(cols_A):
                result[i][j] += A[i][k] * B[k][j]
    
    return result

result = matrix_multiply(data['matrix_a'], data['matrix_b'])
""",
        "sample_data": {
            "matrix_a": [[1, 2], [3, 4]],
            "matrix_b": [[5, 6], [7, 8]]
        }
    },
    
    "data_processing": {
        "type": TaskType.DATA_ANALYSIS,
        "name": "Data Processing",
        "description": "Process and analyze numerical data",
        "code": """
import statistics

def analyze_data(numbers):
    return {
        'count': len(numbers),
        'sum': sum(numbers),
        'mean': statistics.mean(numbers),
        'median': statistics.median(numbers),
        'std_dev': statistics.stdev(numbers) if len(numbers) > 1 else 0,
        'min': min(numbers),
        'max': max(numbers)
    }

result = analyze_data(data['numbers'])
""",
        "sample_data": {"numbers": list(range(1, 10001))}
    },
    
    "text_analysis": {
        "type": TaskType.FILE_PROCESSING,
        "name": "Text File Analysis",
        "description": "Analyze text content and count words, lines, characters",
        "code": """
def analyze_text(text_content):
    lines = text_content.split('\\n')
    words = text_content.split()
    return {
        'line_count': len(lines),
        'word_count': len(words),
        'char_count': len(text_content),
        'char_count_no_spaces': len(text_content.replace(' ', '')),
        'avg_words_per_line': len(words) / len(lines) if lines else 0
    }

result = analyze_text(data['text'])
""",
        "sample_data": {"text": "This is a sample text.\\nIt has multiple lines.\\nEach line contains words."}
    },
    
    "csv_processing": {
        "type": TaskType.FILE_PROCESSING,
        "name": "CSV Data Processing",
        "description": "Process CSV-like data and calculate statistics",
        "code": """
def process_csv_data(rows):
    if not rows:
        return {'error': 'No data provided'}
    
    # Assume first row is header
    headers = rows[0] if rows else []
    data_rows = rows[1:] if len(rows) > 1 else []
    
    result = {
        'total_rows': len(data_rows),
        'columns': len(headers),
        'column_names': headers
    }
    
    # Try to calculate numeric statistics for each column
    if data_rows:
        numeric_stats = {}
        for col_idx in range(len(headers)):
            try:
                values = [float(row[col_idx]) for row in data_rows if col_idx < len(row)]
                if values:
                    numeric_stats[headers[col_idx]] = {
                        'min': min(values),
                        'max': max(values),
                        'sum': sum(values),
                        'avg': sum(values) / len(values)
                    }
            except:
                pass
        result['numeric_columns'] = numeric_stats
    
    return result

result = process_csv_data(data['rows'])
""",
        "sample_data": {
            "rows": [
                ["Name", "Age", "Score"],
                ["Alice", "25", "85"],
                ["Bob", "30", "92"],
                ["Charlie", "28", "78"]
            ]
        }
    },
    
    "image_stats": {
        "type": TaskType.IMAGE_PROCESSING,
        "name": "Image Statistics",
        "description": "Calculate statistics from image pixel data",
        "code": """
def analyze_image_data(pixels):
    if not pixels or not pixels[0]:
        return {'error': 'Invalid image data'}
    
    height = len(pixels)
    width = len(pixels[0])
    total_pixels = height * width
    
    # Flatten pixel values
    all_values = []
    for row in pixels:
        for pixel in row:
            if isinstance(pixel, (list, tuple)):
                all_values.extend(pixel)
            else:
                all_values.append(pixel)
    
    if not all_values:
        return {'error': 'No pixel data'}
    
    return {
        'width': width,
        'height': height,
        'total_pixels': total_pixels,
        'min_value': min(all_values),
        'max_value': max(all_values),
        'avg_value': sum(all_values) / len(all_values),
        'total_values': len(all_values)
    }

result = analyze_image_data(data['pixels'])
""",
        "sample_data": {
            "pixels": [
                [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                [[128, 128, 128], [200, 200, 200], [50, 50, 50]]
            ]
        }
    },
    
    "color_histogram": {
        "type": TaskType.IMAGE_PROCESSING,
        "name": "Color Histogram",
        "description": "Generate color histogram from image data",
        "code": """
def generate_histogram(pixels):
    histogram = {}
    pixel_count = 0
    
    for row in pixels:
        for pixel in row:
            if isinstance(pixel, (list, tuple)) and len(pixel) >= 3:
                # RGB color
                r, g, b = pixel[0], pixel[1], pixel[2]
                color_key = f"RGB({r},{g},{b})"
                histogram[color_key] = histogram.get(color_key, 0) + 1
                pixel_count += 1
            elif isinstance(pixel, (int, float)):
                # Grayscale
                histogram[pixel] = histogram.get(pixel, 0) + 1
                pixel_count += 1
    
    # Convert to percentages
    histogram_percent = {k: (v / pixel_count * 100) if pixel_count > 0 else 0 
                         for k, v in histogram.items()}
    
    return {
        'total_pixels': pixel_count,
        'unique_colors': len(histogram),
        'histogram': histogram,
        'histogram_percent': histogram_percent
    }

result = generate_histogram(data['pixels'])
""",
        "sample_data": {
            "pixels": [
                [[255, 0, 0], [0, 255, 0], [0, 0, 255]],
                [[255, 0, 0], [0, 255, 0], [128, 128, 128]]
            ]
        }
    }
}
