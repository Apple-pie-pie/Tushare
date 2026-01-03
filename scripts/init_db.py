"""数据库初始化脚本"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.core import db

def init_database():
    """初始化数据库表结构"""
    logger.info("开始初始化数据库...")
    
    try:
        # 创建核心面板表
        db.create_daily_panel_table()
        db.create_funda_panel_table()
        
        logger.success("✅ 数据库初始化完成")
        logger.info("""
        已创建以下表：
        - etl_state: ETL状态管理
        - endpoint_capabilities: 接口能力记录
        - run_history: 运行历史
        - daily_panel: 交易日面板（核心）
        - funda_panel: 财务面板（核心）
        """)
        
        return True
    
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Tushare数据面板系统 - 数据库初始化")
    logger.info("=" * 60)
    
    success = init_database()
    
    if success:
        logger.info("\n下一步：")
        logger.info("1. 配置 .env 文件（复制 .env.example 并填入Token）")
        logger.info("2. 运行 python scripts/probe_capabilities.py 探测接口能力")
        logger.info("3. 启动UI：streamlit run ui/app.py")
    else:
        logger.error("初始化失败，请检查错误信息")
        sys.exit(1)
