"""配置管理模块"""
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

# 加载环境变量
load_dotenv()

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# Tushare配置
TUSHARE_TOKEN = os.getenv("TUSHARE_TOKEN", "")
TUSHARE_POINTS = int(os.getenv("TUSHARE_POINTS", "5000"))

# 数据库配置
DATABASE_PATH = PROJECT_ROOT / os.getenv("DATABASE_PATH", "data/serve/tushare.duckdb")

# 限频配置（5000+积分）
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "500"))
RATE_LIMIT_DAILY = int(os.getenv("RATE_LIMIT_DAILY", "999999"))

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 数据路径
DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN_PATH = PROJECT_ROOT / "data" / "clean"
DATA_SERVE_PATH = PROJECT_ROOT / "data" / "serve"

# 接口注册表
ENDPOINT_REGISTRY_PATH = PROJECT_ROOT / "config" / "endpoint_registry.yaml"


def load_endpoint_registry() -> dict:
    """加载接口注册表"""
    with open(ENDPOINT_REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_available_endpoints(user_points: int = None) -> dict:
    """获取当前积分可用的接口列表"""
    if user_points is None:
        user_points = TUSHARE_POINTS
    
    registry = load_endpoint_registry()
    available = {}
    
    for api_name, config in registry.items():
        if config['permission_mode'] == 'independent':
            # 独立权限接口需要单独开通
            available[api_name] = {**config, 'user_can_access': False}
        elif config['permission_mode'] == 'points':
            # 积分门槛接口
            can_access = user_points >= config['min_points']
            available[api_name] = {**config, 'user_can_access': can_access}
        else:
            available[api_name] = config
    
    return available


# 确保数据目录存在
DATA_RAW_PATH.mkdir(parents=True, exist_ok=True)
DATA_CLEAN_PATH.mkdir(parents=True, exist_ok=True)
DATA_SERVE_PATH.mkdir(parents=True, exist_ok=True)
