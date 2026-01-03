# 技术文档

本目录包含 Tushare 数据面板系统的详细技术文档。

---

## 📚 文档清单

### [数据设计规范 (DATA_DESIGN.md)](DATA_DESIGN.md)
**必读**：系统核心设计原则与最佳实践

**内容概要**：
1. ✅ 绝对索引 vs 相对索引（为什么禁止用 offset/limit 做主键）
2. 📋 主键设计规范（daily_panel / funda_panel 等）
3. 🔄 增量策略（按交易日循环 vs 按股票循环）
4. 🔑 权限管理（积分门槛、独立权限、探测机制）
5. 💾 幂等写入（Upsert模式、批内去重）
6. 📊 数据质量保障（完整性检查、连续性检查）

**适用场景**：
- 新增数据表时，如何定义主键
- 开发ETL流程时，如何设计增量逻辑
- 遇到权限问题时，如何处理降级
- 数据出现重复或缺失时，如何排查

---

### [接口完整清单 (API_COMPLETE_LIST.md)](API_COMPLETE_LIST.md)
**必读**：所有 Tushare 接口的积分分类与主键定义

**内容概要**：
1. 🔓 120积分可用（1个基础接口）
2. 🔓 2000积分可用（约35个核心接口）
   - 基础数据、行情数据、财务数据、指数数据、基金数据
3. 🔓 4000/5000/10000积分额外可用
4. 🔒 独立权限接口（分钟线、港美股、新闻公告）
5. 📊 本系统已实现的25个核心接口
6. 🔧 如何添加新接口（yaml注册 + extractors实现）

**适用场景**：
- 查询自己的积分能用哪些接口
- 判断新需求需要多少积分
- 添加新接口到系统
- 向上级申请积分升级时的依据

---

## 🔗 快速导航

| 你想做什么 | 查看哪个文档 | 具体章节 |
|-----------|-------------|---------|
| 设计新的数据表 | [DATA_DESIGN.md](DATA_DESIGN.md) | 第2节：主键设计规范 |
| 实现增量拉取 | [DATA_DESIGN.md](DATA_DESIGN.md) | 第3节：增量策略 |
| 处理权限问题 | [DATA_DESIGN.md](DATA_DESIGN.md) | 第4节：权限管理 |
| 查询可用接口 | [API_COMPLETE_LIST.md](API_COMPLETE_LIST.md) | 按积分分类章节 |
| 添加新接口 | [API_COMPLETE_LIST.md](API_COMPLETE_LIST.md) | 第8节：如何添加新接口 |
| 排查数据重复 | [DATA_DESIGN.md](DATA_DESIGN.md) | 第7节：数据质量保障 |

---

## 💡 最佳实践速查

### ✅ 主键设计

```sql
-- 行情类
PRIMARY KEY (ts_code, trade_date)

-- 财务类
PRIMARY KEY (ts_code, end_date, ann_date)

-- 指数成分
PRIMARY KEY (index_code, con_code, trade_date)
```

### ✅ 增量拉取

```python
# 正确：按交易日循环
for trade_date in trade_dates:
    df = api.daily(trade_date=trade_date)  # 一次拉全市场
    save_to_db(df)

# 错误：按股票循环
for ts_code in stock_list:  # ❌ 慢且易重复
    df = api.daily(ts_code=ts_code, start_date='...', end_date='...')
```

### ✅ 权限处理

```python
# 探测接口能力
status, msg = client.probe_endpoint('daily')

# 无权限时友好提示
if status == 'no_permission':
    st.warning(f"⚠️ 需要 {min_points} 积分")
    return None  # 返回空，不崩溃
```

### ✅ 幂等写入

```python
# 批内去重
df = df.drop_duplicates(subset=['ts_code', 'trade_date'], keep='last')

# 数据库Upsert
db.upsert_dataframe(df, 'daily_panel', pk_fields=['ts_code', 'trade_date'])
```

---

## 🚀 开发流程建议

### 新增数据需求时

1. **确定积分档位**：查 [API_COMPLETE_LIST.md](API_COMPLETE_LIST.md)
2. **设计主键**：参考 [DATA_DESIGN.md](DATA_DESIGN.md) 第2节
3. **注册接口**：在 `config/endpoint_registry.yaml` 添加
4. **实现提取器**：在 `src/etl/extractors.py` 添加方法
5. **测试探测**：运行 `python scripts/probe_capabilities.py`
6. **添加UI入口**：在 Data Studio 页面添加按钮

### 数据质量出问题时

1. **检查主键重复**：运行 [DATA_DESIGN.md](DATA_DESIGN.md) 第7.1节的SQL
2. **检查日期缺口**：运行 第7.2节的SQL
3. **检查异常值**：运行 第7.3节的SQL
4. **查看运行历史**：在 UI 的 Data Studio → 运行历史 查看

---

## 📖 推荐阅读顺序

### 新手入门
1. 先读 [API_COMPLETE_LIST.md](API_COMPLETE_LIST.md) 了解有哪些接口
2. 再读 [DATA_DESIGN.md](DATA_DESIGN.md) 的第1-2节（索引与主键）
3. 实操：运行系统，拉取数据，观察数据库表结构

### 进阶开发
1. 精读 [DATA_DESIGN.md](DATA_DESIGN.md) 的第3-5节（增量、权限、幂等）
2. 按照 [API_COMPLETE_LIST.md](API_COMPLETE_LIST.md) 第8节添加新接口
3. 实现自定义面板构建逻辑

### 生产运维
1. 精读 [DATA_DESIGN.md](DATA_DESIGN.md) 第7节（数据质量保障）
2. 设置定时任务（cron）自动增量更新
3. 监控 etl_state 表的 watermark 与错误

---

**这两份文档是系统设计的核心，建议打印或收藏！**
