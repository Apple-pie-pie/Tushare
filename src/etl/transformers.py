"""数据转换器（清洗、规范化）"""
import pandas as pd
from loguru import logger


class DataTransformer:
    """数据转换器（字段规范化、类型转换）"""
    
    @staticmethod
    def normalize_daily(df: pd.DataFrame) -> pd.DataFrame:
        """规范化日线数据"""
        if df is None or len(df) == 0:
            return df
        
        # 日期转换
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        
        # 数值类型转换
        numeric_cols = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 去重（按主键）
        df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        
        return df
    
    @staticmethod
    def normalize_daily_basic(df: pd.DataFrame) -> pd.DataFrame:
        """规范化每日指标"""
        if df is None or len(df) == 0:
            return df
        
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        
        # 数值转换
        numeric_cols = ['turnover_rate', 'turnover_rate_f', 'volume_ratio', 
                        'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm',
                        'total_share', 'float_share', 'free_share',
                        'total_mv', 'circ_mv']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        return df
    
    @staticmethod
    def normalize_adj_factor(df: pd.DataFrame) -> pd.DataFrame:
        """规范化复权因子"""
        if df is None or len(df) == 0:
            return df
        
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        
        if 'adj_factor' in df.columns:
            df['adj_factor'] = pd.to_numeric(df['adj_factor'], errors='coerce')
        
        df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')
        return df
    
    @staticmethod
    def compute_adj_price(daily_df: pd.DataFrame, adj_df: pd.DataFrame) -> pd.DataFrame:
        """计算复权价格"""
        if daily_df is None or adj_df is None:
            return daily_df
        
        # 合并复权因子
        merged = pd.merge(
            daily_df,
            adj_df[['ts_code', 'trade_date', 'adj_factor']],
            on=['ts_code', 'trade_date'],
            how='left'
        )
        
        # 计算后复权价格
        if 'close' in merged.columns and 'adj_factor' in merged.columns:
            merged['adj_close'] = merged['close'] * merged['adj_factor']
        
        return merged
    
    @staticmethod
    def normalize_financial(df: pd.DataFrame) -> pd.DataFrame:
        """规范化财务数据"""
        if df is None or len(df) == 0:
            return df
        
        # 日期转换
        date_cols = ['end_date', 'ann_date', 'f_ann_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
        
        # 去重（按主键：ts_code + end_date + ann_date）
        df = df.drop_duplicates(subset=['ts_code', 'end_date', 'ann_date'], keep='last')
        
        return df
