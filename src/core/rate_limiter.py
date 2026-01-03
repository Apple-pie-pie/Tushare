"""限频器：防止触碰Tushare API限制"""
import time
from collections import deque
from typing import Optional
from loguru import logger
from config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_DAILY


class RateLimiter:
    """速率限制器（基于滑动窗口）"""
    
    def __init__(self, calls_per_minute: int = RATE_LIMIT_PER_MINUTE, 
                 calls_per_day: int = RATE_LIMIT_DAILY):
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        
        # 分钟窗口（60秒）
        self.minute_window = deque()
        self.minute_duration = 60
        
        # 日窗口（24小时）
        self.day_window = deque()
        self.day_duration = 86400
        
        logger.info(f"限频器初始化: {calls_per_minute}次/分钟, {calls_per_day}次/天")
    
    def _clean_old_calls(self, window: deque, duration: int):
        """清理过期的调用记录"""
        now = time.time()
        while window and now - window[0] > duration:
            window.popleft()
    
    def acquire(self):
        """获取调用许可（阻塞等待）"""
        while True:
            now = time.time()
            
            # 清理过期记录
            self._clean_old_calls(self.minute_window, self.minute_duration)
            self._clean_old_calls(self.day_window, self.day_duration)
            
            # 检查分钟限制
            if len(self.minute_window) >= self.calls_per_minute:
                sleep_time = self.minute_duration - (now - self.minute_window[0]) + 0.1
                logger.warning(f"达到分钟限制，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)
                continue
            
            # 检查日限制
            if len(self.day_window) >= self.calls_per_day:
                sleep_time = self.day_duration - (now - self.day_window[0]) + 1
                logger.error(f"达到日限制，等待 {sleep_time:.1f} 秒")
                time.sleep(sleep_time)
                continue
            
            # 记录本次调用
            self.minute_window.append(now)
            self.day_window.append(now)
            
            # 添加小延迟防止瞬间突发
            time.sleep(0.12)  # 500次/分钟 = 120ms间隔
            break
    
    def get_stats(self) -> dict:
        """获取限频统计"""
        now = time.time()
        self._clean_old_calls(self.minute_window, self.minute_duration)
        self._clean_old_calls(self.day_window, self.day_duration)
        
        return {
            "calls_last_minute": len(self.minute_window),
            "calls_today": len(self.day_window),
            "minute_limit": self.calls_per_minute,
            "day_limit": self.calls_per_day,
            "minute_remaining": self.calls_per_minute - len(self.minute_window),
            "day_remaining": self.calls_per_day - len(self.day_window),
        }


# 全局单例
rate_limiter = RateLimiter()
