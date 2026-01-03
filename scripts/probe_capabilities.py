"""探测Tushare接口能力"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from config import get_available_endpoints, TUSHARE_POINTS
from src.core import get_client, db

def probe_all_endpoints():
    """探测所有接口的实际可用性"""
    logger.info("开始探测接口能力...")
    
    try:
        client = get_client()
        endpoints = get_available_endpoints(TUSHARE_POINTS)
        
        logger.info(f"当前积分档位: {TUSHARE_POINTS}")
        logger.info(f"待探测接口数: {len(endpoints)}")
        
        results = {
            "available": [],
            "no_permission": [],
            "error": [],
        }
        
        for i, (api_name, config) in enumerate(endpoints.items(), 1):
            logger.info(f"[{i}/{len(endpoints)}] 探测: {api_name}")
            
            status, message = client.probe_endpoint(api_name)
            
            # 记录到数据库
            db.execute("""
                INSERT OR REPLACE INTO endpoint_capabilities 
                (api_name, min_points, permission_mode, status, message, last_probe_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                api_name,
                config.get('min_points'),
                config.get('permission_mode'),
                status,
                message
            ))
            
            # 分类统计
            results[status].append(api_name)
            
            # 打印结果
            status_emoji = {"available": "✅", "no_permission": "⚠️", "error": "❌"}
            logger.info(f"  {status_emoji.get(status, '?')} {status}: {message}")
        
        # 统计结果
        logger.success("\n探测完成！统计结果：")
        logger.info(f"✅ 可用: {len(results['available'])} 个")
        logger.info(f"⚠️ 无权限: {len(results['no_permission'])} 个")
        logger.info(f"❌ 错误: {len(results['error'])} 个")
        
        # 打印无权限列表
        if results['no_permission']:
            logger.warning("\n以下接口无权限：")
            for api in results['no_permission']:
                logger.warning(f"  - {api}")
        
        return True
    
    except Exception as e:
        logger.error(f"探测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Tushare数据面板系统 - 接口能力探测")
    logger.info("=" * 60)
    
    success = probe_all_endpoints()
    
    if success:
        logger.success("\n✅ 探测完成，结果已保存到数据库")
        logger.info("可在UI的 API Catalog 页面查看详细结果")
    else:
        logger.error("探测失败，请检查错误信息")
        sys.exit(1)
