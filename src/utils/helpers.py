"""工具函数"""
from datetime import datetime, timedelta


def format_date(date_str: str, output_format: str = "%Y%m%d") -> str:
    """统一日期格式"""
    if isinstance(date_str, str):
        if len(date_str) == 8:  # YYYYMMDD
            dt = datetime.strptime(date_str, "%Y%m%d")
        elif len(date_str) == 10:  # YYYY-MM-DD
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            return date_str
    else:
        dt = date_str
    
    return dt.strftime(output_format)


def get_recent_trade_dates(days: int = 30) -> tuple[str, str]:
    """获取最近N个自然日的起止日期（YYYYMMDD）"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")
