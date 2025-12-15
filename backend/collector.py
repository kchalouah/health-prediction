import psutil
import GPUtil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.has_gpu = False
        try:
            self.gpus = GPUtil.getGPUs()
            if self.gpus:
                self.has_gpu = True
                logger.info(f"Detected {len(self.gpus)} GPU(s)")
        except Exception as e:
            logger.warning(f"GPU monitoring disabled: {e}")

    def get_metrics(self) -> Dict[str, Any]:
        """Collects comprehensive system metrics."""
        metrics = {}

        # CPU
        metrics['cpu_usage'] = psutil.cpu_percent(interval=None)
        metrics['cpu_freq'] = psutil.cpu_freq().current if psutil.cpu_freq() else 0
        
        # Memory
        mem = psutil.virtual_memory()
        metrics['memory_usage'] = mem.percent
        metrics['memory_available_mb'] = mem.available / (1024 * 1024)

        # Disk
        disk = psutil.disk_usage('/')
        metrics['disk_usage'] = disk.percent
        
        try:
            disk_io = psutil.disk_io_counters()
            metrics['disk_read_bytes'] = disk_io.read_bytes
            metrics['disk_write_bytes'] = disk_io.write_bytes
        except Exception:
            metrics['disk_read_bytes'] = 0
            metrics['disk_write_bytes'] = 0

        # Network
        try:
            net = psutil.net_io_counters()
            metrics['net_sent_bytes'] = net.bytes_sent
            metrics['net_recv_bytes'] = net.bytes_recv
        except Exception:
            metrics['net_sent_bytes'] = 0
            metrics['net_recv_bytes'] = 0
            
        # GPU (if available)
        if self.has_gpu:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0] # Monitor primary GPU
                    metrics['gpu_usage'] = gpu.load * 100
                    metrics['gpu_memory_usage'] = gpu.memoryUtil * 100
                    metrics['gpu_temp'] = gpu.temperature
                else:
                    self._zero_gpu(metrics)
            except Exception:
                 self._zero_gpu(metrics)
        else:
            self._zero_gpu(metrics)

        # Process Count
        metrics['process_count'] = len(psutil.pids())

        return metrics

    def _zero_gpu(self, metrics):
        metrics['gpu_usage'] = 0.0
        metrics['gpu_memory_usage'] = 0.0
        metrics['gpu_temp'] = 0.0
