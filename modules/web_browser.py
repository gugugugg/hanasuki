# -*- coding: utf-8 -*-
# =================================================================
# Module: Hanasuki Web Browser Engine (Academic Purify Edition)
# Version: V2.2.0
# Function: 提供具身化联网搜索与深度网页内容提取，内置学术白名单加权。
# =================================================================

import os
import asyncio
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class WebBrowser:
    def __init__(self, config=None):
        """初始化学术浏览器引擎"""
        self.config = config or {}
        # 1. 硬核黑名单：彻底拦截电子垃圾站点
        self.blacklist = [
            "zhihu.com", "csdn.net", "baidu.com", "jianshu.com", 
            "51cto.com", "jb51.net", "360.cn", "so.com", "xiaohongshu.com"
        ]
        # 2. 学术白名单：优先采集高价值信源
        self.whitelist = [
            "arxiv.org", "openreview.net", "pytorch.org", "docs.python.org", 
            "numpy.org", "medium.com", "towardsdatascience.com", "distill.pub", 
            "stanford.edu", "mit.edu", "berkeley.edu", "github.com"
        ]
        
        # 浏览器启动配置
        self.browser_args = {
            "headless": True,
            "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        }
        print("[Web] 🌐 学术浏览器模块已就绪，护盾算法加载完毕捏！")

    def _is_blacklisted(self, url):
        """检查 URL 是否在黑名单中"""
        domain = urlparse(url).netloc.lower()
        return any(bad_site in domain for bad_site in self.blacklist)

    def _is_whitelisted(self, url):
        """检查 URL 是否在学术白名单中"""
        domain = urlparse(url).netloc.lower()
        return any(good_site in domain for good_site in self.whitelist)

    def search(self, query):
        """
        执行学术净化搜索。
        注：内核 main.py 会自动在 query 后追加 -site 算子，
        这里进行二次物理过滤以确保万无一失！
        """
        print(f"[Web] 🔍 正在进行学术深度检索: {query}")
        search_results = []
        
        try:
            with sync_playwright() as p:
                # 启动 Chromium 引擎
                browser = p.chromium.launch(**self.browser_args)
                page = browser.new_page()
                
                # 使用 DuckDuckGo 或 Bing 进行搜索（避免百度干扰）
                search_url = f"https://www.bing.com/search?q={query}"
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # 提取搜索结果链接和摘要
                # 这里针对 Bing 的 DOM 结构进行精准抓取
                items = page.query_selector_all("li.b_algo")
                
                for item in items:
                    title_el = item.query_selector("h2 a")
                    snippet_el = item.query_selector("p")
                    
                    if title_el:
                        title = title_el.inner_text()
                        link = title_el.get_attribute("href")
                        snippet = snippet_el.inner_text() if snippet_el else ""
                        
                        # 物理拦截：如果搜索引擎不小心吐出了黑名单站点，直接丢弃
                        if self._is_blacklisted(link):
                            continue
                        
                        # 学术加权：标记高质量资源
                        is_academic = self._is_whitelisted(link)
                        prefix = "⭐ [学术高价值] " if is_academic else "[通识] "
                        
                        search_results.append({
                            "title": prefix + title,
                            "url": link,
                            "snippet": snippet,
                            "is_academic": is_academic
                        })
                
                browser.close()
                
        except Exception as e:
            return f"错误：搜索执行失败。详情: {str(e)}"

        # 排序：优先展示白名单资源捏
        search_results.sort(key=lambda x: x['is_academic'], reverse=True)
        
        if not search_results:
            return "提示：未找到符合学术纯净度要求的结果。请尝试更换关键词。"
            
        # 格式化输出给 Hanasuki 查阅捏
        output = "【搜索简报 (已过滤噪音)】\n"
        for i, res in enumerate(search_results[:5], 1):
            output += f"{i}. {res['title']}\n   链接: {res['url']}\n   摘要: {res['snippet']}\n\n"
        
        return output

    def fetch_page(self, url):
        """
        深入抓取指定网页的内容并进行脱水处理。
        """
        if self._is_blacklisted(url):
            return "错误：该域名已被大大列入黑名单，拒绝访问！"
            
        print(f"[Web] 📑 正在提取网页深度内容: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(**self.browser_args)
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page = context.new_page()
                
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                # 获取网页 HTML 源码
                content = page.content()
                browser.close()
                
                # 使用 BeautifulSoup 进行脱水（去除脚本、样式、广告）
                soup = BeautifulSoup(content, "html.parser")
                
                # 移除干扰标签
                for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script_or_style.decompose()
                
                # 获取纯净正文
                raw_text = soup.get_text(separator="\n")
                lines = [line.strip() for line in raw_text.splitlines() if len(line.strip()) > 20]
                clean_text = "\n".join(lines[:100]) # 限制长度，防止上下文溢出
                
                return f"【网页正文内容 - 来自 {url}】\n\n{clean_text}"
                
        except Exception as e:
            return f"错误：网页抓取失败捏。可能存在反爬机制。详情: {str(e)}"

    def execute(self, params):
        """
        工具调度入口，由 ModuleManager 调用。
        支持 'search' 和 'browse' 两种子动作。
        """
        # 优先从 params 获取动作，默认为 search 
        action = params.get('action', 'search')
        
        if action == 'search' or 'query' in params:
            query = params.get('query') or params.get('Query')
            if not query:
                return "错误：搜索任务缺少 'query' 参数。"
            return self.search(query)
            
        elif action == 'browse' or 'url' in params:
            url = params.get('url') or params.get('URL')
            if not url:
                return "错误：浏览任务缺少 'url' 参数。"
            return self.fetch_page(url)
            
        else:
            return f"错误：WebBrowser 不支持操作 '{action}' 捏。请检查 JSON 指令。"

# 测试代码（仅在直接运行此文件时触发）
if __name__ == "__main__":
    browser = WebBrowser()
    # 模拟搜索代数学定义
    # print(browser.search("代数学的学术定义"))