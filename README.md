# 📈 Tushare 数据面板系统

**🏠 100%本地运行 | 无需服务器 | 数据存储在本机**

模仿 Tableau Prep / Alteryx（数据整合）与 TradingView / 同花顺（股票终端）的**本地数据分析工具**

> ⚠️ **这是本地应用，不会上传任何数据到云端**  
> - 所有数据存储在 `data/` 目录的 DuckDB 数据库中  
> - Token 保存在本地 `.env` 文件，不会外传  
> - Streamlit 只在本机运行（默认 `localhost:8501`）

---

## ✨ 核心特性

### 🏠 Market Terminal（股票分析终端）
- ✅ 自选股列表管理
- ✅ K线图与技术指标（MA5/MA20）
- ✅ 每日指标（PE/PB/市值/换手率）
- ✅ 估值卡片与走势
- 🔲 筛选器（后续版本）
- 🔲 多图布局（路线B）

### 🔧 Data Studio（数据整合工作台）
- ✅ 按交易日拉取全市场行情
- ✅ 批量拉取日期范围
- ✅ 面板构建（daily_panel / funda_panel）
- ✅ 增量水位管理（断点续跑）
- 🔲 可视化拖拽Canvas（路线B）

### 📊 API Catalog（接口目录）
- ✅ 40+接口注册表（5000+积分可用范围）
- ✅ 权限透明（积分门槛 / 独立权限）
- ✅ 主键 / 增量字段定义
- ✅ 接口能力探测

### ⚙️ Settings（系统设置）
- ✅ Token配置与测试
- ✅ 积分查询与到期日期
- ✅ 数据库统计

---

## 🚀 快速开始（本地使用）

### 方式1：从GitHub克隆（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/Apple-pie-pie/Tushare.git
cd Tushare

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置Token
cp .env.example .env
# 用文本编辑器打开 .env，填入你的 Tushare Token

# 5. 初始化数据库
python scripts/init_db.py

# 6. 启动应用（本地运行）
streamlit run ui/app.py
```

浏览器自动打开 `http://localhost:8501`（只在你的电脑上运行）

### 方式2：下载ZIP包使用

```bash
# 1. 从GitHub下载ZIP并解压
# 2. 打开终端，进入解压目录
cd Tushare-main

# 3-6. 同上（安装依赖、配置Token、初始化、启动）
```

---

## 📋 本地使用流程

### 首次使用（冷启动）

1. **配置Token**（本地保存）
   - 进入 Settings 页面
   - 输入你的 Tushare Token（从 https://tushare.pro 获取）
   - 点击"保存配置"→ Token 会保存到本地 `.env` 文件
   - 测试连接，查看你的积分

2. **拉取基础数据**（存储在本地）
   - 进入 Data Studio
   - 拉取交易日历（2010-至今）
   - 拉取股票列表
   - 数据会存储在 `data/serve/tushare.duckdb`

3. **拉取行情数据**
   - 选择日期范围，批量拉取日线行情
   - 建议先拉取最近30-90天测试
   - 所有数据都在本地 DuckDB

4. **构建面板**
   - 对拉取的日期执行"批量构建面板"
   - 生成 daily_panel（合并行情+指标+复权）

5. **开始分析**
   - 进入 Market Terminal
   - 添加自选股，查看K线图
   - 所有查询都在本地数据库

### 日常使用

每天打开应用：
```bash
# 进入项目目录
cd Tushare

# 激活虚拟环境（如果使用）
source venv/bin/activate  # Windows: venv\Scripts\activate

# 启动应用
streamlit run ui/app.py
```

更新昨日数据：
1. 进入 Data Studio
2. 选择昨天的日期
3. 点击"拉取单日行情"
4. 点击"构建面板"

---

## 🔒 数据安全说明

### ✅ 本地存储，不上传云端
- **Token**：保存在本地 `.env` 文件，不会提交到 Git（已添加到 `.gitignore`）
- **数据库**：存储在 `data/serve/tushare.duckdb`（本地文件）
- **网络请求**：只调用 Tushare API 拉取数据，不会上传到任何其他服务器
- **Streamlit**：只在本机运行（`localhost:8501`），不会暴露到公网

### ⚠️ 使用建议
- **不要把 `.env` 文件上传到 GitHub**（已配置 `.gitignore` 保护）
- **数据库文件可以备份**：直接复制 `data/` 目录即可
- **分享给他人**：只分享代码，不要分享 `.env` 和 `data/` 目录

**GitHub使用流程**：
1. 先在本地测试所有功能
2. 成功后下载使用
3. Token始终保存在你自己的电脑上，**不会配置到网站上**

---

## 📐 数据设计与接口清单

### ✅ 绝对索引保障
**本系统强制使用绝对索引，禁止相对索引**：
- **交易日面板**：PRIMARY KEY (`ts_code`, `trade_date`) - 股票代码+交易日期
- **财务面板**：PRIMARY KEY (`ts_code`, `end_date`, `ann_date`) - 股票代码+报告期+公告日期
- **禁止使用**：OFFSET、LIMIT、自增ID等相对索引方式

详细规范请查看：**[docs/DATA_DESIGN.md](docs/DATA_DESIGN.md)**

### 📋 接口完整清单
系统支持 **50+** Tushare接口，按积分分级：
- **120积分**：日线行情（1个接口）
- **2000积分**：股票列表、财务三表、日线指标等（35+接口）
- **4000-5000积分**：分钟线、财务明细等（10+接口）
- **10000+积分**：Level-2行情、高频数据等（5+接口）
- **独立权限**：新闻公告、港美股数据等（需单独申请）

完整清单请查看：**[docs/API_COMPLETE_LIST.md](docs/API_COMPLETE_LIST.md)**

### 🔐 权限管理机制
- **权限探测**：首次使用时自动探测所有接口权限，结果存入 `endpoint_capabilities` 表
- **友好降级**：无权限接口显示"⚠️ 需要X积分"，不会报错崩溃
- **UI展示**：在"API Catalog"页面查看你有权限的接口（绿色✓）和无权限的接口（红色✗）

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
# 进入项目目录
cd Tushare

# 激活虚拟环境（如果使用）
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置Token

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的 Tushare Token
# TUSHARE_TOKEN=your_token_here
# TUSHARE_POINTS=5000
```

### 3️⃣ 初始化数据库

```bash
python scripts/init_db.py
```

### 4️⃣ 启动UI

```bash
streamlit run ui/app.py
```

浏览器将自动打开 `http://localhost:8501`

---

## 🔧 系统架构（本地运行）

```
┌─────────────────────────────────────┐
│  你的电脑（localhost）               │
│                                      │
│  ┌────────────────────────────┐    │
│  │  Streamlit UI              │    │
│  │  (http://localhost:8501)   │    │
│  └──────────┬─────────────────┘    │
│             │                        │
│  ┌──────────▼─────────────────┐    │
│  │  Python 后端逻辑            │    │
│  │  (src/core, src/etl)        │    │
│  └──────────┬─────────────────┘    │
│             │                        │
│  ┌──────────▼─────────────────┐    │
│  │  DuckDB 本地数据库          │    │
│  │  (data/serve/tushare.duckdb)│    │
│  └────────────────────────────┘    │
│                                      │
└──────────────┬───────────────────────┘
               │ 仅此处需要网络
               ▼
    ┌────────────────────┐
    │  Tushare Pro API   │
    │  (拉取股票数据)    │
    └────────────────────┘
```

**数据流向**：
1. 你的电脑 → Tushare API（拉取数据）
2. Tushare API → 你的电脑（返回数据）
3. 数据存储在本地 DuckDB
4. UI 查询本地数据库

**不涉及**：
- ❌ 云服务器部署
- ❌ 数据上传到云端
- ❌ 需要公网IP
- ❌ 需要域名

---

## 📦 分发给他人使用

### 方式1：分享GitHub链接
把仓库地址发给对方：`https://github.com/Apple-pie-pie/Tushare`  
对方按照"快速开始"章节操作即可

### 方式2：打包成ZIP
```bash
# 1. 清理数据和配置（不要分享你的Token和数据）
rm -rf data/serve/*.duckdb
rm .env

# 2. 压缩项目
zip -r Tushare.zip . -x "*.git*" -x "*__pycache__*" -x "venv/*"

# 3. 发送 Tushare.zip 给对方
```

---

## 📋 使用流程

### 首次使用（冷启动）

1. **配置Token**：进入 Settings 页面，输入Token并测试连接
2. **拉取基础数据**：
   - 进入 Data Studio → 拉取交易日历（2010-至今）
   - 拉取股票列表
3. **拉取行情数据**：
   - 选择日期范围，批量拉取日线行情
   - 建议先拉取最近30-90天
4. **构建面板**：
   - 对拉取的日期范围执行"批量构建面板"
   - 生成 daily_panel（供终端查询）
5. **开始分析**：进入 Market Terminal 查看行情

### 日常增量更新

```bash
# 每日定时任务（推荐）
# 1. 拉取昨日/今日行情
# 2. 构建昨日/今日面板
# 3. 查看终端数据
```

---

## 🏗️ 系统架构

### 数据分层
```
┌─────────────────────────────────────┐
│  Tushare Pro API (数据源)            │
└──────────────┬──────────────────────┘
               │
          ┌────▼─────┐
          │  Raw层   │  原始接口数据（可追溯）
          │  (DuckDB)│  raw_daily / raw_daily_basic / raw_adj_factor
          └────┬─────┘
               │
          ┌────▼─────┐
          │ Clean层  │  清洗规范化（字段统一、去重）
          └────┬─────┘
               │
          ┌────▼─────┐
          │ Serve层  │  面板数据（daily_panel / funda_panel）
          │ (DuckDB) │  核心查询表，带主键与索引
          └────┬─────┘
               │
          ┌────▼─────┐
          │    UI    │  Streamlit前端（Market Terminal / Data Studio）
          └──────────┘
```

### 核心设计原则

1. **绝对索引**：`(ts_code, trade_date)` 唯一主键，禁止相对索引
2. **权限透明**：所有接口显示积分门槛与当前状态
3. **增量可恢复**：按日期水位增量，支持断点续跑
4. **限频保护**：500次/分钟（5000+积分档位）

---

## 📂 目录结构

```
Tushare/
├── config/                  # 配置文件
│   ├── settings.py         # 配置管理
│   └── endpoint_registry.yaml  # 接口注册表（25+接口）
├── data/                    # 数据目录（本地存储，不提交到Git）
│   ├── raw/                # 原始数据
│   ├── clean/              # 清洗数据
│   └── serve/              # 服务层（DuckDB数据库）
│       └── tushare.duckdb  # 本地数据库文件
├── docs/                    # 📚 技术文档（必读）
│   ├── README.md           # 文档导航
│   ├── DATA_DESIGN.md      # 数据设计规范（主键、增量、权限）
│   └── API_COMPLETE_LIST.md # 接口完整清单（按积分分类）
├── src/                     # 核心代码
│   ├── core/               # 核心模块（数据库、客户端、限频）
│   │   ├── database.py     # DuckDB管理
│   │   ├── tushare_client.py  # Tushare客户端
│   │   └── rate_limiter.py    # 限频器
│   ├── etl/                # ETL模块（提取、转换、加载）
│   │   ├── extractors.py   # 数据提取
│   │   ├── transformers.py # 数据转换
│   │   └── loaders.py      # 数据加载
│   ├── panel/              # 面板构建（daily_panel、funda_panel）
│   │   ├── daily_panel.py  # 交易日面板
│   │   └── funda_panel.py  # 财务面板
│   └── utils/              # 工具函数
├── ui/                      # Streamlit UI（本地运行）
│   ├── app.py              # 主应用
│   └── pages/              # 多页面
│       ├── 1_🏠_Market_Terminal.py    # 股票终端
│       ├── 2_🔧_Data_Studio.py        # 数据工作台
│       ├── 3_📊_API_Catalog.py        # 接口目录
│       └── 4_⚙️_Settings.py           # 系统设置
├── scripts/                 # 工具脚本
│   ├── init_db.py          # 初始化数据库
│   └── probe_capabilities.py  # 探测接口能力
├── .env.example            # 配置模板
├── .env                    # 你的配置（不提交到Git）
├── .gitignore              # Git忽略配置
├── requirements.txt         # Python依赖
├── start.sh                # 快速启动脚本
└── README.md               # 本文件
```

**重点目录说明**：
- 📚 `docs/` - **技术文档**（主键设计、接口清单、权限管理）
- 💾 `data/` - 本地数据存储（不会提交到Git）
- 🔧 `src/` - 核心业务逻辑（可复用到路线B）
- 🖥️ `ui/` - Streamlit前端（路线A特有）

---
│   │   └── funda_panel.py  # 财务面板
│   └── utils/              # 工具函数
├── ui/                      # Streamlit UI
│   ├── app.py              # 主应用
│   └── pages/              # 多页面
│       ├── 1_🏠_Market_Terminal.py
│       ├── 2_🔧_Data_Studio.py
│       ├── 3_📊_API_Catalog.py
│       └── 4_⚙️_Settings.py
├── scripts/                 # 脚本
│   ├── init_db.py          # 初始化数据库
│   └── probe_capabilities.py  # 探测接口能力
├── requirements.txt         # 依赖
├── .env.example            # 配置模板
└── README.md               # 本文件
```

---

## 📊 数据设计与接口清单

### 🔑 核心设计原则

✅ **绝对索引**：所有表使用 `(ts_code, trade_date)` 等唯一主键  
✅ **权限透明**：每个接口显示积分门槛与当前状态  
✅ **增量可恢复**：按日期水位增量，支持断点续跑  
✅ **幂等写入**：按主键Upsert，可重复运行  

### 📚 详细文档

- **[数据设计规范](docs/DATA_DESIGN.md)**：主键策略、增量模式、权限管理、数据质量保障
- **[接口完整清单](docs/API_COMPLETE_LIST.md)**：所有积分档位的接口列表（120/2000/5000/10000+）

### 核心接口示例

| 接口名 | 类别 | 最低积分 | 主键 | 增量字段 |
|--------|------|---------|------|---------|
| daily | 股票行情 | 120 | (ts_code, trade_date) | trade_date |
| daily_basic | 股票行情 | 2000 | (ts_code, trade_date) | trade_date |
| adj_factor | 股票行情 | 2000 | (ts_code, trade_date) | trade_date |
| income | 财务数据 | 2000 | (ts_code, end_date, ann_date) | ann_date |
| balancesheet | 财务数据 | 2000 | (ts_code, end_date, ann_date) | ann_date |
| cashflow | 财务数据 | 2000 | (ts_code, end_date, ann_date) | ann_date |
| fina_indicator | 财务数据 | 2000 | (ts_code, end_date, ann_date) | ann_date |
| trade_cal | 基础数据 | 2000 | (exchange, cal_date) | cal_date |
| stock_basic | 基础数据 | 2000 | (ts_code) | list_date |

**已实现：25个核心接口** | [完整列表](docs/API_COMPLETE_LIST.md) | [接口配置](config/endpoint_registry.yaml)

---

## 🔧 两条实现路线

### 路线A：快速原型（当前版本）
- ✅ Streamlit + Plotly
- ✅ 步骤式流程（手动运行）
- ✅ DuckDB本地存储
- ⏱️ 开发周期：1-2周

### 路线B：专业版（升级计划）
- 🔲 React + FastAPI
- 🔲 可视化拖拽Canvas（React Flow）
- 🔲 多图布局与联动
- 🔲 Electron桌面应用
- ⏱️ 开发周期：4-8周

**升级时机**：路线A验证完成，业务逻辑稳定后

---

## 🧪 测试与探测

### 探测接口能力
```bash
python scripts/probe_capabilities.py
```

将探测所有接口的实际可用性，并保存到数据库。

### 查询面板数据
```python
from src.panel import DailyPanelBuilder

builder = DailyPanelBuilder()
df = builder.query_panel(
    ts_codes=["000001.SZ"],
    start_date="2024-01-01",
    end_date="2024-12-31"
)
```

---

## ❓ 常见问题（FAQ）

### Q1: 需要服务器吗？
**不需要**。这是 100% 本地应用，只在你的电脑上运行。

### Q2: 数据存在哪里？
**本地 DuckDB 文件**：`data/serve/tushare.duckdb`。你可以：
- 备份：复制 `data/` 目录
- 迁移：把 `data/` 复制到另一台电脑
- 删除：直接删除 `data/` 目录重新开始

### Q3: Token 安全吗？
**安全**。Token 保存在本地 `.env` 文件，已添加到 `.gitignore`，不会被提交到 GitHub。

### Q4: 可以在公司内网使用吗？
**可以**。只要能访问 `tushare.pro` 拉取数据即可。UI 只在本机运行。

### Q5: 多台电脑使用怎么办？
- **方案1**：每台电脑独立安装（各自拉取数据）
- **方案2**：共享 `data/` 目录（通过网盘/NAS同步）
- **方案3**：升级为路线B，部署到内网服务器

### Q6: 如何关闭应用？
在终端按 `Ctrl+C` 即可停止 Streamlit。数据已保存在本地数据库。

### Q7: 卸载怎么办？
直接删除整个 `Tushare/` 目录即可。没有任何系统级安装。

### Q8: 数据拉取很慢？
- 按交易日拉取（推荐）：一天5000股票一次拉完
- 避免按股票代码循环拉取
- 5000+积分限频：500次/分钟

### Q9: 如何备份数据？
```bash
# 备份整个data目录
cp -r data/ data_backup_20260103/

# 或只备份数据库文件
cp data/serve/tushare.duckdb data/serve/tushare_backup.duckdb
```

---

## ❓ 常见问题

### Q1: Token在哪里获取？
访问 [Tushare官网](https://tushare.pro) 注册账号，完成积分任务后在个人中心获取。

### Q2: 没有5000积分怎么办？
- 120积分：可用日线行情（daily），但频次受限
- 2000积分：可用大部分接口（200次/分钟）
- 修改 `.env` 中的 `TUSHARE_POINTS` 配置

### Q3: 数据拉取很慢？
- 按交易日拉取（推荐）：一天5000股票一次拉完
- 避免按股票代码循环拉取
- 5000+积分限频：500次/分钟

### Q4: 报错 "权限不足"？
- 检查 API Catalog 查看接口的最低积分要求
- 部分接口需要独立开通（分钟线、新闻公告等）

### Q5: 如何升级到路线B？
- 当前保持数据层不变（database.py、面板构建逻辑）
- 前端替换为 React + FastAPI
- 参考系统架构文档

---

## 🤝 贡献

欢迎提交 Issue 与 PR！

---

## 📄 许可证

MIT License

---

## � 许可证

MIT License - 可自由使用、修改、分发

---

## 🙏 致谢

- [Tushare Pro](https://tushare.pro) - 数据源
- [Streamlit](https://streamlit.io) - UI框架
- [DuckDB](https://duckdb.org) - 本地数据库

---

**💡 记住：这是 100% 本地应用，你的数据完全在自己掌控中！**
