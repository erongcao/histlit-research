#!/usr/bin/env python3
"""
历史学文献检索工具
支持 OpenAlex、Google Scholar、Crossref
"""

import sys
import json
import urllib.request
import urllib.parse
import time
import os
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional, Set
from pathlib import Path

# 尝试导入requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# 配置文件路径
CONFIG_DIR = Path.home() / ".histlit"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "search_history.json"


class ConfigManager:
    """配置管理器"""
    
    @staticmethod
    def load_config() -> Dict:
        """加载配置文件"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    @staticmethod
    def save_config(config: Dict) -> None:
        """保存配置文件"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class SearchHistory:
    """检索历史管理器"""
    
    @staticmethod
    def load_history(limit: Optional[int] = None) -> List[Dict]:
        """加载检索历史"""
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    if limit:
                        return history[:limit]
                    return history
            except Exception:
                pass
        return []
    
    @staticmethod
    def save_history(history: List[Dict]) -> None:
        """保存检索历史"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def add_search(query: str, databases: List[str], results_count: int,
                   date_range: Optional[str] = None) -> str:
        """添加检索记录"""
        history = SearchHistory.load_history()
        
        search_id = hashlib.md5(
            f"{query}{','.join(databases)}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:8]
        
        record = {
            "id": search_id,
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "databases": databases,
            "date_range": date_range,
            "results_count": results_count
        }
        
        history.insert(0, record)
        history = history[:50]
        SearchHistory.save_history(history)
        return search_id


class OpenAlexSearcher:
    """OpenAlex 检索器（免费、开放）"""
    
    BASE_URL = "https://api.openalex.org/works"
    
    @staticmethod
    def search(query: str, max_results: int = 20,
               date_range: Optional[str] = None,
               fields: Optional[List[str]] = None) -> Dict:
        """
        检索 OpenAlex
        
        Args:
            query: 检索词
            max_results: 最大结果数
            date_range: 时间范围 (YYYY:YYYY)
            fields: 领域过滤 (如 ["History", "Political Science"])
        """
        # 构建查询
        search_params = {
            "search": query,
            "per-page": min(max_results, 25),
            "sort": "relevance_score:desc"
        }
        
        # 添加时间过滤
        filter_parts = []
        if date_range:
            start_year, end_year = date_range.split(":")
            filter_parts.append(f"from_publication_date:{start_year}-01-01")
            filter_parts.append(f"to_publication_date:{end_year}-12-31")
        
        # 添加领域过滤
        if fields:
            field_filter = "|".join(fields)
            filter_parts.append(f"concepts.id:{field_filter}")
        
        if filter_parts:
            search_params["filter"] = ",".join(filter_parts)
        
        try:
            url = f"{OpenAlexSearcher.BASE_URL}?{urllib.parse.urlencode(search_params)}"
            
            headers = {
                "User-Agent": "histlit-research/1.0 (mailto:your_email@example.com)"
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            results = []
            for work in data.get("results", []):
                # 提取作者
                authors = []
                for authorship in work.get("authorships", [])[:5]:
                    author = authorship.get("author", {})
                    name = author.get("display_name", "")
                    if name:
                        authors.append(name)
                
                # 提取期刊/出版社
                host_venue = work.get("host_venue", {}) or work.get("primary_location", {})
                if isinstance(host_venue, dict):
                    journal = host_venue.get("display_name", "N/A")
                else:
                    journal = "N/A"
                
                # 提取年份
                pub_date = work.get("publication_date", "")
                year = work.get("publication_year", "N/A")
                
                # 提取 DOI
                doi = work.get("doi", "")
                
                # 提取 URL
                open_access = work.get("open_access", {})
                url = open_access.get("oa_url", "") or work.get("id", "")
                
                results.append({
                    "id": work.get("id", "").replace("https://openalex.org/", ""),
                    "title": work.get("display_name", "N/A"),
                    "authors": authors if authors else ["N/A"],
                    "journal": journal,
                    "pubdate": str(year) if year else pub_date[:4] if pub_date else "N/A",
                    "doi": doi.replace("https://doi.org/", "") if doi else "",
                    "url": url,
                    "cited_by_count": work.get("cited_by_count", 0),
                    "is_oa": open_access.get("is_oa", False),
                    "database": "OpenAlex"
                })
            
            return {
                "database": "OpenAlex",
                "query": query,
                "total_count": data.get("meta", {}).get("count", 0),
                "returned_count": len(results),
                "results": results,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "database": "OpenAlex",
                "query": query,
                "status": "error",
                "error": {
                    "code": "SEARCH_ERROR",
                    "message": str(e)
                }
            }


class CrossrefSearcher:
    """Crossref 检索器（免费）"""
    
    BASE_URL = "https://api.crossref.org/works"
    
    @staticmethod
    def search(query: str, max_results: int = 20,
               date_range: Optional[str] = None,
               work_type: Optional[str] = "journal-article") -> Dict:
        """
        检索 Crossref
        
        Args:
            query: 检索词
            max_results: 最大结果数
            date_range: 时间范围 (YYYY:YYYY)
            work_type: 文献类型 (journal-article, book, etc.)
        """
        search_params = {
            "query": query,
            "rows": min(max_results, 20),
            "sort": "relevance",
            "order": "desc"
        }
        
        # 添加时间过滤
        if date_range:
            start_year, end_year = date_range.split(":")
            search_params["filter"] = f"from-pub-date:{start_year},until-pub-date:{end_year}"
        
        # 添加类型过滤
        if work_type:
            if "filter" in search_params:
                search_params["filter"] += f",type:{work_type}"
            else:
                search_params["filter"] = f"type:{work_type}"
        
        # 添加邮件（礼貌性，提高速率限制）
        config = ConfigManager.load_config()
        email = config.get("email", "")
        if email:
            search_params["mailto"] = email
        
        try:
            url = f"{CrossrefSearcher.BASE_URL}?{urllib.parse.urlencode(search_params)}"
            
            headers = {
                "User-Agent": "histlit-research/1.0"
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            items = data.get("message", {}).get("items", [])
            
            results = []
            for item in items:
                # 提取作者
                authors = []
                for author in item.get("author", [])[:5]:
                    given = author.get("given", "")
                    family = author.get("family", "")
                    if given and family:
                        authors.append(f"{given} {family}")
                    elif family:
                        authors.append(family)
                
                # 提取期刊
                journal = item.get("container-title", ["N/A"])[0] if item.get("container-title") else "N/A"
                
                # 提取年份
                pub_date = item.get("published-print", {}) or item.get("published-online", {})
                year = pub_date.get("date-parts", [["N/A"]])[0][0] if pub_date else "N/A"
                
                results.append({
                    "doi": item.get("DOI", ""),
                    "title": item.get("title", ["N/A"])[0] if item.get("title") else "N/A",
                    "authors": authors if authors else ["N/A"],
                    "journal": journal,
                    "pubdate": str(year),
                    "url": item.get("URL", ""),
                    "cited_by_count": item.get("is-referenced-by-count", 0),
                    "type": item.get("type", "unknown"),
                    "database": "Crossref"
                })
            
            return {
                "database": "Crossref",
                "query": query,
                "total_count": data.get("message", {}).get("total-results", 0),
                "returned_count": len(results),
                "results": results,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "database": "Crossref",
                "query": query,
                "status": "error",
                "error": {
                    "code": "SEARCH_ERROR",
                    "message": str(e)
                }
            }


class GoogleScholarSearcher:
    """
    Google Scholar 检索器
    注意：Google Scholar 没有官方 API，这里使用 SerpAPI 或其他第三方服务
    或者返回手动搜索链接
    """
    
    @staticmethod
    def search(query: str, max_results: int = 10,
               date_range: Optional[str] = None) -> Dict:
        """
        Google Scholar 检索
        由于没有官方 API，返回搜索链接和基本指导
        """
        # 构建搜索 URL
        search_params = {
            "q": query,
            "hl": "en"
        }
        
        if date_range:
            start_year, end_year = date_range.split(":")
            search_params["as_ylo"] = start_year
            search_params["as_yhi"] = end_year
        
        search_url = f"https://scholar.google.com/scholar?{urllib.parse.urlencode(search_params)}"
        
        return {
            "database": "Google Scholar",
            "query": query,
            "status": "manual_search_required",
            "message": "Google Scholar 没有官方 API，请使用以下链接手动检索",
            "search_url": search_url,
            "note": "建议使用 OpenAlex 或 Crossref 进行自动检索"
        }


class HistoryDatabaseSearcher:
    """历史学数据库联合检索器"""
    
    def __init__(self):
        pass
    
    def search_openalex(self, query: str, max_results: int = 20,
                        date_range: Optional[str] = None) -> Dict:
        """OpenAlex 检索"""
        # 历史学相关领域
        history_fields = [
            "C144602167",  # History
            "C15708023",   # Political Science
            "C17744445",   # Sociology
            "C138885662"   # Anthropology
        ]
        return OpenAlexSearcher.search(query, max_results, date_range, history_fields)
    
    def search_crossref(self, query: str, max_results: int = 20,
                        date_range: Optional[str] = None) -> Dict:
        """Crossref 检索"""
        return CrossrefSearcher.search(query, max_results, date_range)
    
    def search_scholar(self, query: str, max_results: int = 10,
                       date_range: Optional[str] = None) -> Dict:
        """Google Scholar 检索"""
        return GoogleScholarSearcher.search(query, max_results, date_range)
    
    def search_all(self, query: str, max_results: int = 20,
                   date_range: Optional[str] = None,
                   databases: List[str] = None) -> Dict:
        """多数据库联合检索"""
        if databases is None:
            databases = ["openalex", "crossref"]
        
        results_by_db = {}
        
        if "openalex" in databases:
            time.sleep(0.5)
            results_by_db["openalex"] = self.search_openalex(query, max_results, date_range)
        
        if "crossref" in databases:
            time.sleep(0.5)
            results_by_db["crossref"] = self.search_crossref(query, max_results, date_range)
        
        if "scholar" in databases:
            results_by_db["scholar"] = self.search_scholar(query, max_results, date_range)
        
        # 计算总数
        total_articles = sum(
            db_result.get("returned_count", 0)
            for db_result in results_by_db.values()
            if db_result.get("status") == "success"
        )
        
        # 保存检索历史
        search_id = SearchHistory.add_search(query, databases, total_articles, date_range)
        
        return {
            "query": query,
            "date_range": date_range,
            "databases_searched": databases,
            "search_id": search_id,
            "results_by_database": results_by_db,
            "summary": {
                "total_articles_found": total_articles
            }
        }


def print_help():
    """打印帮助信息"""
    print("""
历史学文献检索工具 (Histlit-Research)

使用方法:
  python3 history_search.py <query> [options]

选项:
  --dbs DATABASES    数据库 (openalex,crossref,scholar)，默认: openalex,crossref
  --max N            最大结果数 (默认: 20)
  --date YYYY:YYYY   时间范围
  --config email     设置邮箱（提高 Crossref 速率限制）
  --history [N]      查看检索历史

示例:
  # 基本检索
  python3 history_search.py "French Revolution"

  # 多数据库检索
  python3 history_search.py "World War II" --dbs openalex,crossref --max 30

  # 限定时间范围
  python3 history_search.py "Cold War" --date 2010:2025

  # 设置邮箱
  python3 history_search.py --config email your_email@example.com

数据库说明:
  - OpenAlex: 免费、开放、推荐首选
  - Crossref: 免费、学术出版元数据
  - Google Scholar: 无API，返回搜索链接
""")


def print_history(limit: int = 10):
    """打印检索历史"""
    history = SearchHistory.load_history(limit)
    
    if not history:
        print("暂无检索历史")
        return
    
    print(f"\n最近 {len(history)} 条检索历史:")
    print("-" * 80)
    for record in history:
        print(f"ID: {record['id']}")
        print(f"时间: {record['timestamp']}")
        print(f"检索词: {record['query']}")
        print(f"数据库: {', '.join(record['databases'])}")
        print(f"结果数: {record['results_count']}")
        if record.get('date_range'):
            print(f"时间范围: {record['date_range']}")
        print("-" * 80)


def main():
    # 处理配置命令
    if len(sys.argv) >= 3 and sys.argv[1] == "--config":
        config_type = sys.argv[2]
        
        if config_type == "email" and len(sys.argv) >= 4:
            config = ConfigManager.load_config()
            config["email"] = sys.argv[3]
            ConfigManager.save_config(config)
            print(f"✅ 邮箱已保存到 {CONFIG_FILE}")
        else:
            print("用法: --config email your_email@example.com")
        sys.exit(0)
    
    # 处理历史命令
    if len(sys.argv) >= 2 and sys.argv[1] == "--history":
        limit = int(sys.argv[2]) if len(sys.argv) >= 3 else 10
        print_history(limit)
        sys.exit(0)
    
    # 显示帮助
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(1)
    
    # 解析参数
    query = sys.argv[1]
    databases = ["openalex", "crossref"]
    max_results = 20
    date_range = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--dbs" and i + 1 < len(sys.argv):
            databases = sys.argv[i + 1].split(",")
            i += 2
        elif sys.argv[i] == "--max" and i + 1 < len(sys.argv):
            max_results = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--date" and i + 1 < len(sys.argv):
            date_range = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # 执行检索
    searcher = HistoryDatabaseSearcher()
    result = searcher.search_all(query, max_results, date_range, databases)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
