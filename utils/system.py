import os
import time

# 用於手動計算 CPU 使用率的快取變數
_last_cpu_time = None
_last_sys_time = None

def get_cpu_usage() -> float:
    """獲取當前 Streamlit 進程的 CPU 使用率。"""
    global _last_cpu_time, _last_sys_time
    try:
        import psutil
        process = psutil.Process(os.getpid())
        # interval=None 能即時以非阻塞 (non-blocking) 的方式回傳自上次呼叫以來的 CPU 使用率
        return process.cpu_percent(interval=None)
    except Exception:
        # 當 psutil 無法使用時，在 Linux 環境下手動計算 CPU
        try:
            with open('/proc/self/stat', 'r') as f:
                stat = f.read().split()
            # 讀取使用者時間 (14) 與系統時間 (15)，單位為 ticks
            utime = int(stat[13])
            stime = int(stat[14])
            ticks_per_sec = os.sysconf(os.SC_CLK_TCK)
            proc_time = (utime + stime) / ticks_per_sec
            
            # 讀取系統開機時間
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.readline().split()[0])
            
            now = time.time()
            if _last_cpu_time is not None and _last_sys_time is not None:
                delta_proc = proc_time - _last_cpu_time
                delta_time = now - _last_sys_time
                if delta_time > 0:
                    cpu_percent = (delta_proc / delta_time) * 100
                    cpu_percent = min(100.0, max(0.0, cpu_percent))
                    _last_cpu_time = proc_time
                    _last_sys_time = now
                    return cpu_percent
            
            _last_cpu_time = proc_time
            _last_sys_time = now
            return 0.0
        except Exception:
            return 0.0

def get_memory_usage() -> tuple[float, float, float]:
    """
    獲取當前進程的 RAM 使用量 (MB) 與使用率。
    回傳: (已使用_mb, 限制_mb, 百分比)
    """
    limit_mb = 1024.0  # Streamlit Community Cloud 的硬性限制為 1GB (1024MB)
    used_mb = 0.0
    
    try:
        # 優先讀取 Linux native 進程資訊，極度輕量
        if os.path.exists('/proc/self/status'):
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        parts = line.split()
                        used_mb = int(parts[1]) / 1024.0  # 轉為 MB
                        break
        
        # 若 VmRSS 未成功讀取，使用 psutil 備援
        if used_mb == 0.0:
            import psutil
            process = psutil.Process(os.getpid())
            used_mb = process.memory_info().rss / (1024.0 * 1024.0)
            
    except Exception:
        used_mb = 0.0
        
    percent = (used_mb / limit_mb) * 100.0 if limit_mb > 0 else 0.0
    return used_mb, limit_mb, percent
