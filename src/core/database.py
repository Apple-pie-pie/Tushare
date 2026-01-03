"""DuckDB数据库管理"""
import duckdb
from pathlib import Path
from typing import Optional
from loguru import logger
from config import DATABASE_PATH


class Database:
    """DuckDB数据库管理器（单例模式）"""
    
    _instance: Optional['Database'] = None
    _conn: Optional[duckdb.DuckDBPyConnection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._conn is None:
            self.connect()
    
    def connect(self):
        """连接数据库"""
        db_path = Path(DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._conn = duckdb.connect(str(db_path))
        logger.info(f"数据库已连接: {db_path}")
        
        # 初始化系统表
        self._init_system_tables()
    
    def _init_system_tables(self):
        """初始化系统表（元数据管理）"""
        # ETL状态表：记录每个接口的增量水位
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS etl_state (
                api_name VARCHAR PRIMARY KEY,
                watermark_value VARCHAR,
                last_success_at TIMESTAMP,
                last_row_count INTEGER,
                last_error VARCHAR,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 接口能力表：记录探测结果
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS endpoint_capabilities (
                api_name VARCHAR PRIMARY KEY,
                min_points INTEGER,
                permission_mode VARCHAR,
                status VARCHAR,
                last_probe_at TIMESTAMP,
                message VARCHAR,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 运行历史表：记录每次拉取任务
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS run_history (
                id INTEGER PRIMARY KEY,
                api_name VARCHAR,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR,
                rows_fetched INTEGER,
                rows_inserted INTEGER,
                error_message VARCHAR,
                parameters VARCHAR
            )
        """)
        
        logger.info("系统表初始化完成")
    
    def create_daily_panel_table(self):
        """创建交易日面板表（核心面板1）"""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_panel (
                ts_code VARCHAR,
                trade_date DATE,
                -- 行情数据
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                pre_close DOUBLE,
                change DOUBLE,
                pct_chg DOUBLE,
                vol DOUBLE,
                amount DOUBLE,
                -- 复权价格
                adj_factor DOUBLE,
                adj_close DOUBLE,
                -- 每日指标
                turnover_rate DOUBLE,
                turnover_rate_f DOUBLE,
                volume_ratio DOUBLE,
                pe DOUBLE,
                pe_ttm DOUBLE,
                pb DOUBLE,
                ps DOUBLE,
                ps_ttm DOUBLE,
                dv_ratio DOUBLE,
                dv_ttm DOUBLE,
                total_share DOUBLE,
                float_share DOUBLE,
                free_share DOUBLE,
                total_mv DOUBLE,
                circ_mv DOUBLE,
                -- 元数据
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ts_code, trade_date)
            )
        """)
        logger.info("daily_panel表已创建")
    
    def create_funda_panel_table(self):
        """创建财务面板表（核心面板2）"""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS funda_panel (
                ts_code VARCHAR,
                end_date DATE,
                ann_date DATE,
                -- 利润表关键指标
                total_revenue DOUBLE,
                operating_profit DOUBLE,
                total_profit DOUBLE,
                n_income DOUBLE,
                n_income_attr_p DOUBLE,
                basic_eps DOUBLE,
                diluted_eps DOUBLE,
                -- 资产负债表关键指标
                total_assets DOUBLE,
                total_liab DOUBLE,
                total_hldr_eqy_exc_min_int DOUBLE,
                -- 现金流量表关键指标
                n_cashflow_act DOUBLE,
                n_cashflow_inv_act DOUBLE,
                n_cash_flows_fnc_act DOUBLE,
                -- 财务指标
                roe DOUBLE,
                roe_waa DOUBLE,
                roe_dt DOUBLE,
                roa DOUBLE,
                grossprofit_margin DOUBLE,
                netprofit_margin DOUBLE,
                assets_turn DOUBLE,
                debt_to_assets DOUBLE,
                current_ratio DOUBLE,
                quick_ratio DOUBLE,
                -- 同比增长
                revenue_yoy DOUBLE,
                profit_yoy DOUBLE,
                netprofit_yoy DOUBLE,
                -- 元数据
                report_type VARCHAR,
                update_flag VARCHAR,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ts_code, end_date, ann_date)
            )
        """)
        logger.info("funda_panel表已创建")
    
    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """获取数据库连接"""
        if self._conn is None:
            self.connect()
        return self._conn
    
    def execute(self, query: str, params: tuple = None):
        """执行SQL"""
        if params:
            return self._conn.execute(query, params)
        return self._conn.execute(query)
    
    def query(self, query: str, params: tuple = None):
        """查询并返回DataFrame"""
        if params:
            return self._conn.execute(query, params).df()
        return self._conn.execute(query).df()
    
    def insert_dataframe(self, df, table_name: str, if_exists: str = "append"):
        """插入DataFrame（幂等写入）"""
        if if_exists == "replace":
            self._conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        self._conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df")
        
        if if_exists == "append":
            self._conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
        
        logger.info(f"已插入 {len(df)} 行到 {table_name}")
    
    def upsert_dataframe(self, df, table_name: str, pk_fields: list):
        """Upsert操作（按主键去重覆盖）"""
        # 先删除主键冲突的记录
        pk_condition = " AND ".join([f"t.{field} = s.{field}" for field in pk_fields])
        
        self._conn.execute(f"""
            DELETE FROM {table_name} AS t
            WHERE EXISTS (
                SELECT 1 FROM df AS s
                WHERE {pk_condition}
            )
        """)
        
        # 再插入新数据
        self._conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
        logger.info(f"已upsert {len(df)} 行到 {table_name}")
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("数据库连接已关闭")


# 全局单例
db = Database()
