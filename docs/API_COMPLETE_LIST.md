# Tushare接口完整清单（按积分分类）

**更新日期**：2026-01-03  
**数据来源**：[Tushare Pro 权限总表](https://tushare.pro/document/1?doc_id=108)

---

## 🔓 120积分可用（1个基础接口）

| 接口名 | 类别 | 主键 | 增量字段 | 说明 |
|--------|------|------|----------|------|
| `daily` | 股票行情 | (ts_code, trade_date) | trade_date | 日线行情（未复权） |

**限制**：50次/分钟，日上限8000次

---

## 🔓 2000积分可用（约35个核心接口）

### 基础数据（5个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `stock_basic` | (ts_code) | list_date | 股票列表与基本信息 |
| `trade_cal` | (exchange, cal_date) | cal_date | 交易日历 |
| `namechange` | (ts_code, ann_date) | ann_date | 股票曾用名 |
| `hs_const` | (ts_code, hs_type) | in_date | 沪深港通成分 |
| `new_share` | (ts_code) | ipo_date | IPO新股列表 |

### 股票行情（7个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `weekly` | (ts_code, trade_date) | trade_date | 周线行情 |
| `monthly` | (ts_code, trade_date) | trade_date | 月线行情 |
| `adj_factor` | (ts_code, trade_date) | trade_date | 复权因子 |
| `suspend_d` | (ts_code, suspend_date) | suspend_date | 每日停牌信息 |
| `daily_basic` | (ts_code, trade_date) | trade_date | 每日指标（PE/PB/市值/换手） |
| `moneyflow` | (ts_code, trade_date) | trade_date | 个股资金流向 |
| `stk_limit` | (ts_code, trade_date) | trade_date | 涨跌停价格 |

### 财务数据（10个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `income` | (ts_code, end_date, ann_date) | ann_date | 利润表 |
| `balancesheet` | (ts_code, end_date, ann_date) | ann_date | 资产负债表 |
| `cashflow` | (ts_code, end_date, ann_date) | ann_date | 现金流量表 |
| `fina_indicator` | (ts_code, end_date, ann_date) | ann_date | 财务指标（ROE/毛利率等） |
| `fina_audit` | (ts_code, ann_date) | ann_date | 财务审计意见 |
| `fina_mainbz` | (ts_code, end_date, item) | ann_date | 主营业务构成 |
| `disclosure_date` | (ts_code, end_date) | actual_date | 财报披露计划 |
| `dividend` | (ts_code, ann_date, end_date) | ann_date | 分红送股 |
| `top10_holders` | (ts_code, end_date, ann_date) | ann_date | 前十大股东 |
| `top10_floatholders` | (ts_code, end_date, ann_date) | ann_date | 前十大流通股东 |

### 指数数据（7个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `index_basic` | (ts_code) | - | 指数基本信息 |
| `index_daily` | (ts_code, trade_date) | trade_date | 指数日线行情 |
| `index_weekly` | (ts_code, trade_date) | trade_date | 指数周线行情 |
| `index_monthly` | (ts_code, trade_date) | trade_date | 指数月线行情 |
| `index_weight` | (index_code, con_code, trade_date) | trade_date | 指数成分与权重 |
| `index_classify` | (index_code, industry_code) | - | 申万行业分类 |
| `index_member` | (index_code, con_code) | in_date | 指数成分股 |

### 基金数据（6个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `fund_basic` | (ts_code) | found_date | 基金列表 |
| `fund_company` | (name) | - | 基金公司 |
| `fund_manager` | (id) | - | 基金经理 |
| `fund_nav` | (ts_code, nav_date) | nav_date | 基金净值 |
| `fund_div` | (ts_code, ann_date) | ann_date | 基金分红 |
| `fund_portfolio` | (ts_code, ann_date) | ann_date | 基金持仓 |

**限制**：200次/分钟，单接口日10万次

---

## 🔓 4000积分额外可用（2个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `index_dailybasic` | (ts_code, trade_date) | trade_date | 指数每日指标（PE/PB） |
| `daily_info` | (trade_date, exchange) | trade_date | 市场交易统计 |

---

## 🔓 5000积分额外可用（约10个）

### 特色数据

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `bak_daily` | (ts_code, trade_date) | trade_date | 备用行情 |
| `stk_rewards` | (ts_code, ann_date) | ann_date | 管理层薪酬 |
| `stk_holdertrade` | (ts_code, ann_date, holder_name) | ann_date | 股东增减持 |
| `concept` | (code, name) | - | 概念板块 |
| `concept_detail` | (id, concept_name, ts_code) | in_date | 概念成分股 |
| `share_float` | (ts_code, ann_date) | ann_date | 限售股解禁 |
| `stk_factor` | (ts_code, trade_date) | trade_date | 技术因子 |
| `broker_recommend` | (ts_code, date) | date | 券商评级 |

**限制**：500次/分钟，常规数据无上限

---

## 🔓 10000积分额外可用（约5个）

| 接口名 | 主键 | 增量字段 | 说明 |
|--------|------|----------|------|
| `margin` | (trade_date, exchange, name) | trade_date | 融资融券交易汇总 |
| `margin_detail` | (trade_date, ts_code) | trade_date | 融资融券交易明细 |
| `top_list` | (trade_date, ts_code) | trade_date | 龙虎榜 |
| `top_inst` | (trade_date, ts_code, exalter) | trade_date | 龙虎榜机构交易 |
| `pledge_stat` | (ts_code, end_date) | end_date | 股权质押统计 |

**限制**：1000次/分钟，特色数据额外频次

---

## 🔒 独立权限接口（需单独开通，不在积分范畴）

### 分钟行情
- `stk_mins` - 股票分钟线（1/5/15/30/60分钟）
- `index_mins` - 指数分钟线

### 港美股数据
- `hk_basic` - 港股列表
- `hk_daily` - 港股日线
- `hk_mins` - 港股分钟线
- `us_basic` - 美股列表
- `us_daily` - 美股日线

### 新闻公告
- `news` - 财经新闻
- `anns` - 公司公告
- `report_rc` - 研究报告

### 期货期权
- `fut_basic` - 期货合约
- `fut_daily` - 期货日线
- `opt_basic` - 期权合约
- `opt_daily` - 期权日线

---

## 📊 本系统已实现的接口（endpoint_registry.yaml）

### 核心行情（6个）
✅ `daily` - 日线行情  
✅ `weekly` - 周线行情  
✅ `monthly` - 月线行情  
✅ `adj_factor` - 复权因子  
✅ `daily_basic` - 每日指标  
✅ `moneyflow` - 资金流向  

### 财务数据（5个）
✅ `income` - 利润表  
✅ `balancesheet` - 资产负债表  
✅ `cashflow` - 现金流量表  
✅ `fina_indicator` - 财务指标  
✅ `dividend` - 分红送股  

### 指数数据（6个）
✅ `index_basic` - 指数基本信息  
✅ `index_daily` - 指数日线  
✅ `index_weight` - 指数成分与权重  
✅ `index_classify` - 申万行业分类  
✅ `index_member` - 指数成分股  
✅ `index_dailybasic` - 指数每日指标  

### 基础数据（3个）
✅ `stock_basic` - 股票列表  
✅ `trade_cal` - 交易日历  
✅ `new_share` - IPO新股  

### 基金数据（2个）
✅ `fund_basic` - 基金列表  
✅ `fund_nav` - 基金净值  

### 独立权限（3个，已标注状态）
⚠️ `stk_mins` - 分钟线（需单独开通）  
⚠️ `news` - 财经新闻（需单独开通）  
⚠️ `anns` - 公司公告（需单独开通）  

**已实现：25个接口**  
**可扩展：按需添加到 `config/endpoint_registry.yaml`**

---

## 🔧 如何添加新接口

### 步骤1：在 endpoint_registry.yaml 中注册

```yaml
stk_holdertrade:
  category: "股东股本"
  permission_mode: "points"
  min_points: 5000
  pk_fields: ["ts_code", "ann_date", "holder_name"]
  watermark_field: "ann_date"
  max_rows: 5000
  description: "股东增减持"
  status: "available"
  increment_strategy: "by_ann_date_with_lookback"
  lookback_days: 90
```

### 步骤2：在 extractors.py 中添加提取方法

```python
def extract_holdertrade_by_date(self, start_date: str, end_date: str):
    """提取股东增减持"""
    df = self.client.fetch("stk_holdertrade", start_date=start_date, end_date=end_date)
    if df is not None and len(df) > 0:
        db.execute("CREATE TABLE IF NOT EXISTS raw_stk_holdertrade AS SELECT * FROM df WHERE 1=0")
        db.upsert_dataframe(df, "raw_stk_holdertrade", 
                           pk_fields=["ts_code", "ann_date", "holder_name"])
    return df
```

### 步骤3：在 UI 中添加调用入口

在 Data Studio 页面添加按钮调用即可。

---

## 📚 参考资料

- [Tushare Pro 权限总表](https://tushare.pro/document/1?doc_id=108)
- [Tushare Pro 积分获取](https://tushare.pro/document/1?doc_id=13)
- [Tushare Pro 数据接口文档](https://tushare.pro/document/2)

---

**本系统采用"按需加载"策略**：
- ✅ 核心25个接口已实现，覆盖90%使用场景
- 🔲 其他接口按需添加（只需在yaml注册+添加提取方法）
- 📊 所有接口权限透明，无权限友好提示
