"""财务面板构建器"""
import pandas as pd
from loguru import logger
from src.core import db
from src.etl import DataExtractor, DataTransformer, DataLoader


class FundaPanelBuilder:
    """财务面板构建器（三大报表 + 财务指标合并）"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
    
    def build_for_period(self, period: str, start_date: str = None, end_date: str = None):
        """为指定报告期或公告日范围构建面板"""
        logger.info(f"构建财务面板: period={period}, {start_date}~{end_date}")
        
        # 1. 提取利润表（简化版，完整版需要三表+指标）
        income_df = self.extractor.extract_income_by_period(period, start_date, end_date)
        
        if income_df is None or len(income_df) == 0:
            logger.warning("无财务数据")
            return
        
        # 2. 规范化
        income_df = self.transformer.normalize_financial(income_df)
        
        # 3. 选择关键字段（简化版）
        key_cols = ['ts_code', 'end_date', 'ann_date', 'f_ann_date', 'report_type',
                    'total_revenue', 'operating_profit', 'total_profit', 
                    'n_income', 'n_income_attr_p', 'basic_eps', 'diluted_eps',
                    'revenue_yoy', 'operate_profit_yoy', 'net_profit_yoy']
        
        available_cols = [col for col in key_cols if col in income_df.columns]
        panel = income_df[available_cols].copy()
        
        # 4. 加载到面板表
        self.loader.load_to_funda_panel(panel)
        
        logger.info(f"财务面板构建完成: {len(panel)} 条")
    
    def query_panel(self, ts_codes: list = None, start_date: str = None, 
                    end_date: str = None, limit: int = 1000) -> pd.DataFrame:
        """查询财务面板"""
        conditions = []
        params = []
        
        if ts_codes:
            placeholders = ','.join(['?' for _ in ts_codes])
            conditions.append(f"ts_code IN ({placeholders})")
            params.extend(ts_codes)
        
        if start_date:
            conditions.append("end_date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("end_date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT * FROM funda_panel
            WHERE {where_clause}
            ORDER BY ann_date DESC, ts_code
            LIMIT {limit}
        """
        
        return db.query(query, tuple(params) if params else None)
