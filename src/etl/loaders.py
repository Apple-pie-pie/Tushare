"""数据加载器（写入服务层）"""
from loguru import logger
from src.core import db


class DataLoader:
    """数据加载器（写入面板表）"""
    
    @staticmethod
    def load_to_daily_panel(df, mode: str = "upsert"):
        """加载到交易日面板"""
        if df is None or len(df) == 0:
            logger.warning("没有数据可加载到 daily_panel")
            return
        
        if mode == "upsert":
            db.upsert_dataframe(df, "daily_panel", pk_fields=["ts_code", "trade_date"])
        else:
            db.insert_dataframe(df, "daily_panel", if_exists="append")
        
        logger.info(f"已加载 {len(df)} 行到 daily_panel")
    
    @staticmethod
    def load_to_funda_panel(df, mode: str = "upsert"):
        """加载到财务面板"""
        if df is None or len(df) == 0:
            logger.warning("没有数据可加载到 funda_panel")
            return
        
        if mode == "upsert":
            db.upsert_dataframe(df, "funda_panel", pk_fields=["ts_code", "end_date", "ann_date"])
        else:
            db.insert_dataframe(df, "funda_panel", if_exists="append")
        
        logger.info(f"已加载 {len(df)} 行到 funda_panel")
