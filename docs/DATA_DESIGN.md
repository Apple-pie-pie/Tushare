# 数据设计规范：绝对索引与权限管理

## 1. 核心原则：绝对索引，禁止相对索引

### ✅ 正确做法：绝对索引

所有数据表**必须**使用业务语义明确的唯一主键，不允许相对索引参与身份标识。

#### 行情类数据
```sql
-- 正确：用股票代码+交易日期作为唯一标识
PRIMARY KEY (ts_code, trade_date)

-- 示例：000001.SZ 在 2024-01-03 的行情数据
ts_code='000001.SZ', trade_date='2024-01-03'
```

#### 财务类数据
```sql
-- 正确：用股票代码+报告期+公告日期作为唯一标识
PRIMARY KEY (ts_code, end_date, ann_date)

-- 示例：000001.SZ 2023年报（2024年4月公告）
ts_code='000001.SZ', end_date='2023-12-31', ann_date='2024-04-20'
```

#### 指数成分
```sql
-- 正确：用指数代码+成分代码+日期
PRIMARY KEY (index_code, con_code, trade_date)
```

### ❌ 禁止做法：相对索引

```python
# 错误示例1：用 offset/limit 当身份
df = fetch_data(offset=100, limit=50)  # ❌ offset 会因为数据更新而变化

# 错误示例2：用行号当主键
df['id'] = range(len(df))  # ❌ 行号不稳定

# 错误示例3：用自增ID当唯一标识
CREATE TABLE data (id INTEGER PRIMARY KEY AUTOINCREMENT, ...)  # ❌ ID 无业务含义
```

### ✅ 相对索引的正确用途

相对索引**只能**用于分页取数，**不能**参与唯一性判断：

```python
# 正确：用于分页拉取，但不作为主键
for offset in range(0, total, 1000):
    df = api.fetch(offset=offset, limit=1000)
    # 拉取后，用 (ts_code, trade_date) 去重和入库
    df = df.drop_duplicates(subset=['ts_code', 'trade_date'])
```

---

## 2. 主键设计规范

### 2.1 daily_panel（交易日面板）

```sql
CREATE TABLE daily_panel (
    ts_code VARCHAR,           -- 股票代码（必需）
    trade_date DATE,           -- 交易日期（必需）
    
    -- 行情数据
    open DOUBLE,
    close DOUBLE,
    -- ... 其他字段
    
    PRIMARY KEY (ts_code, trade_date)  -- 唯一约束
);
```

**唯一性保证**：
- 一只股票在同一个交易日只能有一条行情记录
- 停牌/未上市：记录不存在（不用 NULL 填充）
- 复牌/上市后：新增记录

**查询示例**：
```python
# 查询单只股票的历史行情
df = db.query("""
    SELECT * FROM daily_panel
    WHERE ts_code = '000001.SZ'
      AND trade_date >= '2024-01-01'
      AND trade_date <= '2024-12-31'
    ORDER BY trade_date
""")
```

### 2.2 funda_panel（财务面板）

```sql
CREATE TABLE funda_panel (
    ts_code VARCHAR,           -- 股票代码
    end_date DATE,             -- 报告期结束日
    ann_date DATE,             -- 实际公告日期
    
    -- 财务数据
    total_revenue DOUBLE,
    net_income DOUBLE,
    -- ... 其他字段
    
    PRIMARY KEY (ts_code, end_date, ann_date)  -- 三元组唯一
);
```

**唯一性保证**：
- 同一公司的同一报告期，可能多次公告（更正、补充）
- `(ts_code, end_date, ann_date)` 三元组唯一标识一次披露
- 查询"最新公告版本"：按 `ann_date DESC` 取第一条

**查询示例（避免未来函数）**：
```python
# 查询某日期能看到的最新财务数据（已公告的）
df = db.query("""
    SELECT * FROM funda_panel
    WHERE ts_code = '000001.SZ'
      AND ann_date <= '2024-06-30'  -- 只看6月30日前公告的
      AND end_date >= '2023-01-01'
    ORDER BY end_date DESC, ann_date DESC
""")
```

### 2.3 其他核心表主键

| 表名 | 主键 | 说明 |
|------|------|------|
| `trade_cal` | `(exchange, cal_date)` | 交易日历（沪深分开记录） |
| `stock_basic` | `(ts_code)` | 股票基础信息（可选加 `snapshot_date` 保留历史） |
| `index_weight` | `(index_code, con_code, trade_date)` | 指数成分与权重 |
| `raw_daily` | `(ts_code, trade_date)` | 原始日线数据 |
| `raw_daily_basic` | `(ts_code, trade_date)` | 原始每日指标 |
| `raw_adj_factor` | `(ts_code, trade_date)` | 原始复权因子 |

---

## 3. 增量策略：按日期水位，而非股票循环

### ❌ 错误模式：按股票循环
```python
# 不推荐（慢且容易重复）
stock_list = ['000001.SZ', '000002.SZ', ...]  # 5000只
for ts_code in stock_list:
    df = api.daily(ts_code=ts_code, start_date='20240101', end_date='20241231')
    # 需要调用5000次，耗时长
```

### ✅ 正确模式：按交易日循环
```python
# 推荐（快且天然去重）
trade_dates = ['20240102', '20240103', ...]  # 约250天/年
for trade_date in trade_dates:
    df = api.daily(trade_date=trade_date)  # 一次拉全市场5000只
    # 只需调用250次，且结果天然按日期去重
```

**Tushare官方推荐**：按 `trade_date` 循环而非 `ts_code` 循环

### 水位管理（增量续跑）

```python
# etl_state 表记录上次成功的日期
last_date = db.query("SELECT watermark_value FROM etl_state WHERE api_name='daily'")

# 从上次位置继续
new_dates = get_trade_dates(start=last_date, end=today)
for date in new_dates:
    df = api.daily(trade_date=date)
    save_to_db(df)
    update_watermark('daily', date)  # 更新水位
```

---

## 4. 权限管理：透明化与降级

### 4.1 权限分类

#### A. 积分门槛接口
| 最低积分 | 频次限制 | 可用接口示例 |
|---------|---------|-------------|
| 120 | 50次/分钟 | daily（非复权日线） |
| 2000 | 200次/分钟 | daily_basic, adj_factor, income, index_daily |
| 5000 | 500次/分钟 | 约90%接口 |
| 10000 | 1000次/分钟 | 全部常规接口 |

#### B. 独立权限接口（需单独开通）
- 分钟行情（`stk_mins`）
- 港美股数据
- 财经新闻（`news`）
- 公司公告（`anns`）

### 4.2 权限探测机制

系统启动时/手动触发时，对每个接口执行**最小请求**：

```python
def probe_endpoint(api_name):
    try:
        # 最小请求（只拉1行测试数据）
        if api_name == 'daily':
            df = api.daily(trade_date='20240102', limit=1)
        elif api_name == 'stock_basic':
            df = api.stock_basic(limit=1)
        # ...
        
        if df is not None and len(df) > 0:
            return "available"  # ✅ 可用
    except Exception as e:
        if "没有权限" in str(e) or "权限不足" in str(e):
            return "no_permission"  # ⚠️ 无权限
        return "error"  # ❌ 其他错误
```

### 4.3 权限降级策略

当接口无权限时：

```python
# UI层：显示友好提示
if status == "no_permission":
    st.warning(f"""
    ⚠️ 接口 {api_name} 无权限
    - 需要积分：{min_points}+
    - 你的积分：{user_points}
    - 解决方案：完成积分任务或购买积分
    """)
    return None  # 返回空数据，不报错

# 数据层：记录状态
db.execute("""
    INSERT INTO endpoint_capabilities 
    (api_name, status, message) 
    VALUES (?, 'no_permission', '需要5000积分')
""")
```

### 4.4 限频保护

```python
class RateLimiter:
    def __init__(self, calls_per_minute=500):
        self.window = deque()  # 滑动窗口
    
    def acquire(self):
        now = time.time()
        # 清理60秒前的记录
        while self.window and now - self.window[0] > 60:
            self.window.popleft()
        
        # 检查是否达到限制
        if len(self.window) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.window[0])
            time.sleep(sleep_time)
        
        self.window.append(now)
```

---

## 5. 幂等写入：防止重复与冲突

### 5.1 Upsert模式

```python
def upsert_dataframe(df, table_name, pk_fields):
    """按主键去重覆盖"""
    # 先删除主键冲突的记录
    pk_condition = " AND ".join([f"t.{f} = s.{f}" for f in pk_fields])
    db.execute(f"""
        DELETE FROM {table_name} AS t
        WHERE EXISTS (
            SELECT 1 FROM df AS s WHERE {pk_condition}
        )
    """)
    
    # 再插入新数据
    db.execute(f"INSERT INTO {table_name} SELECT * FROM df")
```

### 5.2 批内去重

```python
# 拉取前：按主键去重
df = api.daily(trade_date='20240103')
df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')

# 写入：Upsert模式
upsert_dataframe(df, 'raw_daily', pk_fields=['ts_code', 'trade_date'])
```

---

## 6. 完整接口列表（按积分分类）

### 🔓 120积分可用（1个）
- `daily` - 股票日线行情（非复权）

### 🔓 2000积分可用（35个）

**基础数据**
- `stock_basic` - 股票列表
- `trade_cal` - 交易日历
- `namechange` - 股票曾用名
- `hs_const` - 沪深港通成分
- `new_share` - IPO新股列表

**行情数据**
- `weekly` - 周线行情
- `monthly` - 月线行情
- `adj_factor` - 复权因子
- `suspend_d` - 每日停牌
- `daily_basic` - 每日指标（PE/PB/市值）
- `moneyflow` - 个股资金流向
- `stk_limit` - 涨跌停价格

**财务数据**
- `income` - 利润表
- `balancesheet` - 资产负债表
- `cashflow` - 现金流量表
- `fina_indicator` - 财务指标
- `fina_audit` - 财务审计意见
- `fina_mainbz` - 主营业务构成
- `disclosure_date` - 财报披露计划
- `dividend` - 分红送股
- `top10_holders` - 前十大股东
- `top10_floatholders` - 前十大流通股东

**指数数据**
- `index_basic` - 指数基本信息
- `index_daily` - 指数日线
- `index_weekly` - 指数周线
- `index_monthly` - 指数月线
- `index_weight` - 指数成分与权重
- `index_classify` - 申万行业分类
- `index_member` - 指数成分股

**基金数据**
- `fund_basic` - 基金列表
- `fund_company` - 基金公司
- `fund_manager` - 基金经理
- `fund_nav` - 基金净值
- `fund_div` - 基金分红
- `fund_portfolio` - 基金持仓

### 🔓 4000积分额外可用（2个）
- `index_dailybasic` - 指数每日指标（PE/PB）
- `daily_info` - 市场交易统计

### 🔓 5000积分额外可用（约5个）
- `bak_daily` - 备用行情
- `stk_surv` - 股票调查问卷
- 更多特色数据...

### 🔒 独立权限接口（需单独开通）
- `stk_mins` - 分钟行情
- `news` - 财经新闻
- `anns` - 公司公告
- `hk_basic` / `hk_daily` - 港股数据
- `us_basic` / `us_daily` - 美股数据

---

## 7. 数据质量保障

### 7.1 主键完整性检查

```sql
-- 检查主键重复
SELECT ts_code, trade_date, COUNT(*) as cnt
FROM daily_panel
GROUP BY ts_code, trade_date
HAVING cnt > 1;

-- 应返回空结果
```

### 7.2 日期连续性检查

```sql
-- 检查某股票的日期缺口
WITH dates AS (
    SELECT DISTINCT trade_date FROM trade_cal WHERE is_open=1
)
SELECT d.trade_date
FROM dates d
LEFT JOIN daily_panel p 
    ON d.trade_date = p.trade_date AND p.ts_code = '000001.SZ'
WHERE p.ts_code IS NULL
ORDER BY d.trade_date;
```

### 7.3 数据范围检查

```python
# 检查异常值
df = db.query("""
    SELECT ts_code, trade_date, close, pct_chg
    FROM daily_panel
    WHERE pct_chg > 20 OR pct_chg < -20  -- 涨跌超过20%
       OR close <= 0  -- 价格异常
""")
```

---

## 8. 总结：设计清单

✅ **主键设计**
- [ ] 所有表定义 PRIMARY KEY
- [ ] 主键字段具有业务语义
- [ ] 禁止使用自增ID/行号作为唯一标识

✅ **增量策略**
- [ ] 按日期水位（trade_date/ann_date）增量
- [ ] 记录 watermark 到 etl_state 表
- [ ] 支持断点续跑

✅ **权限管理**
- [ ] 接口注册表包含 min_points / permission_mode
- [ ] 启动时探测接口能力
- [ ] 无权限时友好提示，不崩溃

✅ **幂等写入**
- [ ] 批内去重（drop_duplicates）
- [ ] 数据库 Upsert（按PK覆盖）
- [ ] 可重复运行，结果一致

✅ **数据质量**
- [ ] 定期检查主键重复
- [ ] 监控日期缺口
- [ ] 异常值告警

---

**遵循本规范，可确保数据系统长期稳定、可追溯、可恢复。**
