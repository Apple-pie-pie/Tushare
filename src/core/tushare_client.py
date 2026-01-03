"""Tushare客户端封装（带权限探测与错误处理）"""
import tushare as ts
import pandas as pd
from typing import Optional, Dict, Any
from loguru import logger
from retry import retry
from config import TUSHARE_TOKEN, get_available_endpoints
from .rate_limiter import rate_limiter


class TushareClient:
    """Tushare Pro客户端（带权限管理）"""
    
    def __init__(self, token: str = None):
        self.token = token or TUSHARE_TOKEN
        
        if not self.token:
            raise ValueError("Tushare token未配置！请在.env文件中设置TUSHARE_TOKEN")
        
        # 设置token
        ts.set_token(self.token)
        self.pro = ts.pro_api(self.token)
        
        # 加载接口注册表
        self.endpoints = get_available_endpoints()
        
        logger.info(f"Tushare客户端已初始化，token: {self.token[:10]}...")
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取用户积分与到期信息"""
        try:
            df = self.pro.user(token=self.token)
            if df is not None and len(df) > 0:
                user_info = df.iloc[0].to_dict()
                logger.info(f"用户积分: {user_info.get('score', 'N/A')}, 到期: {user_info.get('exp_date', 'N/A')}")
                return user_info
            return None
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def check_endpoint_permission(self, api_name: str) -> tuple[bool, str]:
        """检查接口权限"""
        if api_name not in self.endpoints:
            return False, f"未知接口: {api_name}"
        
        config = self.endpoints[api_name]
        
        if config['permission_mode'] == 'independent':
            return False, f"需要独立开通权限"
        
        if not config.get('user_can_access', False):
            return False, f"需要 {config['min_points']} 积分"
        
        return True, "OK"
    
    @retry(tries=3, delay=2, backoff=2, logger=logger)
    def _call_api(self, api_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """调用API（带重试与限频）"""
        # 限频
        rate_limiter.acquire()
        
        # 调用接口
        api_func = getattr(self.pro, api_name, None)
        if api_func is None:
            raise ValueError(f"接口不存在: {api_name}")
        
        df = api_func(**kwargs)
        
        if df is not None:
            logger.debug(f"{api_name} 返回 {len(df)} 行")
        else:
            logger.warning(f"{api_name} 返回空")
        
        return df
    
    def fetch(self, api_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """统一拉取接口（带权限检查）"""
        # 检查权限
        has_permission, msg = self.check_endpoint_permission(api_name)
        if not has_permission:
            logger.error(f"接口 {api_name} 无权限: {msg}")
            return None
        
        # 调用API
        try:
            df = self._call_api(api_name, **kwargs)
            return df
        except Exception as e:
            logger.error(f"调用 {api_name} 失败: {e}")
            return None
    
    def fetch_by_trade_date(self, api_name: str, trade_date: str, **kwargs) -> Optional[pd.DataFrame]:
        """按交易日拉取（推荐模式）"""
        return self.fetch(api_name, trade_date=trade_date, **kwargs)
    
    def fetch_by_ts_code(self, api_name: str, ts_code: str, start_date: str = None, 
                         end_date: str = None, **kwargs) -> Optional[pd.DataFrame]:
        """按股票代码拉取"""
        params = {"ts_code": ts_code, **kwargs}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self.fetch(api_name, **params)
    
    def fetch_by_date_range(self, api_name: str, start_date: str, end_date: str, 
                            **kwargs) -> Optional[pd.DataFrame]:
        """按日期范围拉取"""
        return self.fetch(api_name, start_date=start_date, end_date=end_date, **kwargs)
    
    def probe_endpoint(self, api_name: str) -> tuple[str, str]:
        """探测接口可用性（轻量请求）"""
        try:
            # 先检查权限配置
            has_permission, msg = self.check_endpoint_permission(api_name)
            if not has_permission:
                return "no_permission", msg
            
            # 尝试最小请求
            config = self.endpoints[api_name]
            
            # 根据不同接口类型构造探测参数
            if 'trade_date' in config.get('pk_fields', []):
                # 行情类：拉最近一个交易日
                df = self._call_api(api_name, trade_date='20240102', limit=1)
            elif api_name in ['stock_basic', 'index_basic', 'fund_basic']:
                # 列表类：只拉1条
                df = self._call_api(api_name, limit=1)
            else:
                # 其它：拉一个测试代码
                df = self._call_api(api_name, ts_code='000001.SZ', limit=1)
            
            if df is not None:
                return "available", f"探测成功，返回 {len(df)} 行"
            else:
                return "error", "返回空数据"
        
        except Exception as e:
            error_msg = str(e)
            if "没有权限" in error_msg or "权限不足" in error_msg:
                return "no_permission", error_msg
            return "error", error_msg
    
    def get_rate_stats(self) -> dict:
        """获取限频统计"""
        return rate_limiter.get_stats()


# 全局单例（延迟初始化，避免启动时token未配置）
_client_instance: Optional[TushareClient] = None

def get_client() -> TushareClient:
    """获取Tushare客户端单例"""
    global _client_instance
    if _client_instance is None:
        _client_instance = TushareClient()
    return _client_instance
