---
name: histlit-research
description: 历史学文献检索工具。支持 OpenAlex、Crossref、Google Scholar 等多数据库检索，用于检索历史学领域的研究进展。
---

# 历史学文献检索工具 (Histlit-Research)

综合历史学文献检索工具，支持多个免费学术数据库，帮助研究者快速获取历史学领域的最新研究进展。

## 核心功能

1. **OpenAlex 检索** - 免费、开放的学术图谱，推荐首选
2. **Crossref 检索** - 学术出版元数据，覆盖范围广
3. **Google Scholar 链接** - 生成搜索链接（无官方 API）
4. **检索历史** - 自动保存检索记录
5. **多数据库联合检索** - 一次检索多个数据库

## 支持的数据库

| 数据库 | 费用 | API | 特点 |
|-------|------|-----|------|
| OpenAlex | 免费 | ✅ 官方 API | 开放、现代化、推荐首选 |
| Crossref | 免费 | ✅ 官方 API | 学术出版元数据权威 |
| Google Scholar | 免费 | ❌ 无官方 API | 覆盖面广，提供搜索链接 |

## 使用场景

### 场景1: 基本检索

```bash
# OpenAlex 检索（默认）
python3 scripts/history_search.py "French Revolution"

# 多数据库检索
python3 scripts/history_search.py "World War II" --dbs openalex,crossref

# 限定时间范围
python3 scripts/history_search.py "Cold War" --date 2010:2025
```

### 场景2: 检索历史

```bash
# 查看检索历史
python3 scripts/history_search.py --history

# 查看最近20条
python3 scripts/history_search.py --history 20
```

### 场景3: 配置邮箱

```bash
# 设置邮箱（提高 Crossref 速率限制）
python3 scripts/history_search.py --config email your_email@example.com
```

## 检索语法

### 基本检索
```bash
python3 scripts/history_search.py "检索词"
```

### 高级选项
```bash
python3 scripts/history_search.py "检索词" \
  --dbs openalex,crossref \
  --max 30 \
  --date 2015:2025
```

### 参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| `--dbs` | 选择数据库 | `openalex,crossref,scholar` |
| `--max` | 最大结果数 | `20` (默认) |
| `--date` | 时间范围 | `2010:2025` |

## 输出格式

### JSON 输出示例

```json
{
  "query": "French Revolution",
  "databases_searched": ["openalex", "crossref"],
  "search_id": "a1b2c3d4",
  "results_by_database": {
    "openalex": {
      "database": "OpenAlex",
      "total_count": 1523,
      "returned_count": 20,
      "results": [
        {
          "id": "W123456789",
          "title": "The French Revolution: A History",
          "authors": ["Author Name"],
          "journal": "Journal of History",
          "pubdate": "2020",
          "doi": "10.xxxx/xxxxx",
          "url": "https://doi.org/10.xxxx/xxxxx",
          "cited_by_count": 45,
          "is_oa": true,
          "database": "OpenAlex"
        }
      ],
      "status": "success"
    }
  },
  "summary": {
    "total_articles_found": 35
  }
}
```

## 数据库对比

### OpenAlex (推荐)

**优势**:
- 完全免费、开放
- 现代化的 API 设计
- 提供引用计数
- 标记开放获取文献
- 支持领域过滤

**限制**:
- 数据覆盖范围较新
- 部分历史文献可能缺失

**适用场景**: 检索近期研究（2010年后）、需要引用分析

### Crossref

**优势**:
- 学术出版元数据权威
- 覆盖传统出版社
- DOI 解析准确

**限制**:
- 速率限制（需提供邮箱）
- 元数据可能不完整

**适用场景**: 检索传统期刊文献、需要准确的出版信息

### Google Scholar

**优势**:
- 覆盖面最广
- 包括灰色文献

**限制**:
- 无官方 API
- 只能生成搜索链接

**适用场景**: 补充检索、查找难以获取的文献

## 检索策略建议

### 1. 组合检索

建议同时使用 OpenAlex 和 Crossref：
```bash
python3 scripts/history_search.py "your topic" --dbs openalex,crossref
```

### 2. 时间范围

限定时间范围提高相关性：
```bash
python3 scripts/history_search.py "French Revolution" --date 2015:2025
```

### 3. 迭代检索

1. 先用宽泛检索词了解领域
2. 根据结果调整检索词
3. 使用更具体的关键词深入检索

## 配置文件

配置文件位置: `~/.histlit/config.json`

```json
{
  "email": "your_email@example.com"
}
```

## 检索历史

历史记录位置: `~/.histlit/search_history.json`

自动保存最近50条检索记录，包含：
- 检索词
- 数据库
- 时间范围
- 结果数量
- 时间戳

## 注意事项

1. **礼貌使用 API**: 遵守速率限制，不要频繁请求
2. **设置邮箱**: 提高 Crossref 的速率限制
3. **结果验证**: 自动检索结果需要人工验证
4. **补充检索**: 重要研究建议同时手动检索 Google Scholar

## 与其他工具对比

| 工具 | 费用 | 数据库 | 适用领域 |
|-----|------|--------|---------|
| Histlit-Research | 免费 | OpenAlex, Crossref | 历史学 |
| Medlit-Research | 免费 | PubMed, Embase | 医学 |
| Web of Science | 付费 | 综合 | 多学科 |
| Scopus | 付费 | 综合 | 多学科 |

## 未来计划

- [ ] 添加 JSTOR API 支持（需订阅）
- [ ] 添加导出功能（CSV, BibTeX）
- [ ] 添加去重功能
- [ ] 添加全文获取功能
- [ ] 添加批判性评价工具

## 相关资源

- [OpenAlex 文档](https://docs.openalex.org/)
- [Crossref API 文档](https://api.crossref.org/)
- [Google Scholar](https://scholar.google.com/)

## 引用

使用本工具检索到的文献，请按照各数据库的要求进行引用。

---

*Histlit-Research - 让历史学研究更高效*
