"""数据提取器（按接口注册表批量拉取）"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger
from config import load_endpoint_registry
from src.core import get_client, db


class DataExtractor:
    """数据提取器（按日期水位增量拉取）"""
    
    def __init__(self):
        self.client = get_client()
        self.registry = load_endpoint_registry()
    
    def get_last_watermark(self, api_name: str) -> Optional[str]:
        """获取上次成功的水位值"""
        result = db.query(
            "SELECT watermark_value FROM etl_state WHERE api_name = ?",
            (api_name,)
        )
        if len(result) > 0:
            return result.iloc[0]['watermark_value']
        return None
    
    def update_watermark(self, api_name: str, watermark: str, row_count: int):
        """更新水位记录"""
        db.execute("""
            INSERT OR REPLACE INTO etl_state (api_name, watermark_value, last_success_at, last_row_count)
            VALUES (?, ?, ?, ?)
        """, (api_name, watermark, datetime.now(), row_count))
    
    def extract_trade_calendar(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """提取交易日历（基础数据）"""
        if start_date is None:
            start_date = "20100101"
        if end_date is None:
            end_date = datetime.now().strftime("%Y%m%d")
        
        logger.info(f"提取交易日历: {start_date} ~ {end_date}")
        df = self.client.fetch("trade_cal", start_date=start_date, end_date=end_date)
        
        if df is not None and len(df) > 0:
            # 存入数据库
            db.execute("CREATE TABLE IF NOT EXISTS trade_cal AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "trade_cal", pk_fields=["exchange", "cal_date"])
            logger.info(f"交易日历已更新: {len(df)} 条")
        
        return df
    
    def extract_stock_basic(self) -> pd.DataFrame:
        """提取股票列表"""
        logger.info("提取股票基本信息")
        df = self.client.fetch("stock_basic")
        
        if df is not None and len(df) > 0:
            # 添加快照日期
            df['snapshot_date'] = datetime.now().strftime("%Y%m%d")
            
            db.execute("CREATE TABLE IF NOT EXISTS stock_basic AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "stock_basic", pk_fields=["ts_code"])
            logger.info(f"股票列表已更新: {len(df)} 只")
        
        return df
    
    def extract_daily_by_date(self, trade_date: str) -> pd.DataFrame:
        """按交易日提取日线行情（推荐模式）"""
        logger.info(f"提取日线行情: {trade_date}")
        df = self.client.fetch_by_trade_date("daily", trade_date=trade_date)
        
        if df is not None and len(df) > 0:
            db.execute("CREATE TABLE IF NOT EXISTS raw_daily AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "raw_daily", pk_fields=["ts_code", "trade_date"])
            self.update_watermark("daily", trade_date, len(df))
            logger.info(f"日线行情已存储: {len(df)} 条")
        
        return df
    
    def extract_daily_basic_by_date(self, trade_date: str) -> pd.DataFrame:
        """按交易日提取每日指标"""
        logger.info(f"提取每日指标: {trade_date}")
        df = self.client.fetch_by_trade_date("daily_basic", trade_date=trade_date)
        
        if df is not None and len(df) > 0:
            db.execute("CREATE TABLE IF NOT EXISTS raw_daily_basic AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "raw_daily_basic", pk_fields=["ts_code", "trade_date"])
            self.update_watermark("daily_basic", trade_date, len(df))
            logger.info(f"每日指标已存储: {len(df)} 条")
        
        return df
    
    def extract_adj_factor_by_date(self, trade_date: str) -> pd.DataFrame:
        """按交易日提取复权因子"""
        logger.info(f"提取复权因子: {trade_date}")
        df = self.client.fetch_by_trade_date("adj_factor", trade_date=trade_date)
        
        if df is not None and len(df) > 0:
            db.execute("CREATE TABLE IF NOT EXISTS raw_adj_factor AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "raw_adj_factor", pk_fields=["ts_code", "trade_date"])
            self.update_watermark("adj_factor", trade_date, len(df))
            logger.info(f"复权因子已存储: {len(df)} 条")
        
        return df
    
    def extract_income_by_period(self, period: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """提取利润表（按报告期或公告日）"""
        logger.info(f"提取利润表: period={period}, {start_date}~{end_date}")
        
        if period == 'ann_date' and start_date and end_date:
            df = self.client.fetch("income", start_date=start_date, end_date=end_date)
        else:
            df = self.client.fetch("income", period=period)
        
        if df is not None and len(df) > 0:
            db.execute("CREATE TABLE IF NOT EXISTS raw_income AS SELECT * FROM df WHERE 1=0")
            db.upsert_dataframe(df, "raw_income", pk_fields=["ts_code", "end_date", "ann_date"])
            logger.info(f"利润表已存储: {len(df)} 条")
        
        return df
    
    def get_trading_dates(self, start_date: str, end_date: str) -> List[str]:
        """获取日期范围内的所有交易日"""
        df = db.query("""
            SELECT cal_date FROM trade_cal
            WHERE cal_date >= ? AND cal_date <= ? AND is_open = 1
            ORDER BY cal_date
        """, (start_date, end_date))
        
        if len(df) > 0:
            return df['cal_date'].tolist()
        return []
