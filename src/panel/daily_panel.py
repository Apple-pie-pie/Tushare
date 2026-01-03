"""交易日面板构建器"""
import pandas as pd
from loguru import logger
from src.core import db
from src.etl import DataExtractor, DataTransformer, DataLoader


class DailyPanelBuilder:
    """交易日面板构建器（daily + daily_basic + adj_factor 合并）"""
    
    def __init__(self):
        self.extractor = DataExtractor()
        self.transformer = DataTransformer()
        self.loader = DataLoader()
    
    def build_for_date(self, trade_date: str):
        """为单个交易日构建面板"""
        logger.info(f"构建 {trade_date} 的交易日面板")
        
        # 1. 提取三张表
        daily_df = self.extractor.extract_daily_by_date(trade_date)
        basic_df = self.extractor.extract_daily_basic_by_date(trade_date)
        adj_df = self.extractor.extract_adj_factor_by_date(trade_date)
        
        if daily_df is None or len(daily_df) == 0:
            logger.warning(f"{trade_date} 无行情数据")
            return
        
        # 2. 规范化
        daily_df = self.transformer.normalize_daily(daily_df)
        basic_df = self.transformer.normalize_daily_basic(basic_df)
        adj_df = self.transformer.normalize_adj_factor(adj_df)
        
        # 3. 合并（左连接）
        panel = daily_df.copy()
        
        if basic_df is not None and len(basic_df) > 0:
            panel = pd.merge(panel, basic_df, on=['ts_code', 'trade_date'], how='left', suffixes=('', '_basic'))
        
        if adj_df is not None and len(adj_df) > 0:
            panel = self.transformer.compute_adj_price(panel, adj_df)
        
        # 4. 加载到面板表
        self.loader.load_to_daily_panel(panel)
        
        logger.info(f"{trade_date} 面板构建完成: {len(panel)} 只股票")
    
    def build_for_range(self, start_date: str, end_date: str):
        """批量构建日期范围的面板"""
        trade_dates = self.extractor.get_trading_dates(start_date, end_date)
        
        if not trade_dates:
            logger.warning(f"{start_date}~{end_date} 无交易日")
            return
        
        logger.info(f"开始构建 {len(trade_dates)} 个交易日的面板")
        
        for trade_date in trade_dates:
            try:
                self.build_for_date(trade_date)
            except Exception as e:
                logger.error(f"构建 {trade_date} 失败: {e}")
                continue
        
        logger.info("批量构建完成")
    
    def query_panel(self, ts_codes: list = None, start_date: str = None, 
                    end_date: str = None, limit: int = 1000) -> pd.DataFrame:
        """查询面板数据"""
        conditions = []
        params = []
        
        if ts_codes:
            placeholders = ','.join(['?' for _ in ts_codes])
            conditions.append(f"ts_code IN ({placeholders})")
            params.extend(ts_codes)
        
        if start_date:
            conditions.append("trade_date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("trade_date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
            SELECT * FROM daily_panel
            WHERE {where_clause}
            ORDER BY trade_date DESC, ts_code
            LIMIT {limit}
        """
        
        return db.query(query, tuple(params) if params else None)
