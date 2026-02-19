# -*- coding: utf-8 -*-
# =================================================================
# Project: Hanasuki (花好き) AI Kernel - HERO-A+ Edition
# Version: Beta 1.1
# License: GNU General Public License v3 (GPLv3)
# Copyright (c) 2026 lovesang. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# [MISSION]: 为 Hanasuki 提供学术级的联网能力，实现自动化的噪音过滤与深度知识提取捏！🌸
# [STRATEGY]: 内置学术白名单加权 (Academic Whitelist Weighting) 算法。
# =================================================================

"""
模块名称：Web Browser Engine (Academic Purify Edition)
版本：Beta 1.1 (Academic Release)
作用：Hanasuki 项目的“感官延伸”模块，提供学术净化的联网搜索与具身化网页内容提取捏。

核心特性：
1. 物理屏蔽：硬核黑名单过滤算法，从底层拦截低质量内容的渗透捏。
2. 学术赋能：针对 arXiv、GitHub 等科研信源进行权重加倍捏。
3. 文本脱水：基于 BeautifulSoup 的物理脱水机制，仅为模型提供高密度的纯净正文捏。
"""

import os
import asyncio
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class WebBrowser:
    """
    [HERO-A+ 具身浏览器]:
    管理 Hanasuki 的外部信息获取流。
    不仅具备搜索功能，还能对网页进行“去广告/去干扰”处理，适配 8B 模型的小上下文特性捏。
    """
    def __init__(self, config=None):
        """初始化学术浏览器引擎捏。"""
        self.config = config or {}
        
        # 1. [LOGIC]: 硬核黑名单。
        # 彻底拦截容易产生逻辑噪音、广告或低质量 UGC 的站点捏。
        self.blacklist = [
            "zhihu.com", "csdn.net", "baidu.com", "jianshu.com", 
            "51cto.com", "jb51.net", "360.cn", "so.com", "xiaohongshu.com"
        ]
        
        # 2. [LOGIC]: 学术白名单。
        # 在搜索结果中，这些源将被优先置顶，帮助大大高效收集 AAAI 级别的论文素材捏！
        self.whitelist = [
            "arxiv.org", "openreview.net", "pytorch.org", "docs.python.org", 
            "numpy.org", "medium.com", "towardsdatascience.com", "distill.pub", 
            "stanford.edu", "mit.edu", "berkeley.edu", "github.com"
        ]
        
        # 浏览器启动参数：开启 Headless 模式以节约大大珍贵的 GPU 算力捏
        self.browser_args = {
            "headless": True,
            "args": ["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        }
        print("[Web] 🌐 学术浏览器 Beta 1.1 已就绪，噪音防御算法加载完毕捏！")

    def _is_blacklisted(self, url):
        """[SAFETY]: 物理检查 URL 是否在黑名单屏蔽范围内捏。"""
        domain = urlparse(url).netloc.lower()
        return any(bad_site in domain for bad_site in self.blacklist)

    def _is_whitelisted(self, url):
        """[SAFETY]: 物理检查 URL 是否属于高价值学术信源捏。"""
        domain = urlparse(url).netloc.lower()
        return any(good_site in domain for good_site in self.whitelist)

    def search(self, query):
        """
        [LOGIC]: 执行学术净化搜索捏。
        通过 Playwright 驱动 Chromium 进行物理检索，并应用双向过滤逻辑。
        """
        print(f"[Web] 🔍 正在为大大进行学术深度检索: {query}")
        search_results = []
        
        try:
            with sync_playwright() as p:
                # 物理启动 Chromium 推理环境捏
                browser = p.chromium.launch(**self.browser_args)
                page = browser.new_page()
                
                # [STRATEGY]: 默认使用 Bing 国际版，避开部分国内搜索引擎的广告干扰捏
                search_url = f"https://www.bing.com/search?q={query}"
                page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # 针对 DOM 结构执行精准链路抓取
                items = page.query_selector_all("li.b_algo")
                
                for item in items:
                    title_el = item.query_selector("h2 a")
                    snippet_el = item.query_selector("p")
                    
                    if title_el:
                        title = title_el.inner_text()
                        link = title_el.get_attribute("href")
                        snippet = snippet_el.inner_text() if snippet_el else ""
                        
                        # [GUARD]: 物理拦截逻辑，如果检索到黑名单站点则直接静默丢弃捏
                        if self._is_blacklisted(link):
                            continue
                        
                        # [WEIGHTING]: 执行学术信源加权标记捏
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
            return f"错误：搜索任务执行中断捏。详情: {str(e)}"

        # [SORT]: 排序算法，确保高质量论文资源排在大大的视野最前端捏
        search_results.sort(key=lambda x: x['is_academic'], reverse=True)
        
        if not search_results:
            return "（呜呜... 没找到符合学术纯净度要求的结果，大大换个词试试捏？）"
            
        # 格式化输出给 Hanasuki 的上下文引擎查阅捏
        output = "【搜索简报 (已物理去噪)】\n"
        for i, res in enumerate(search_results[:5], 1):
            output += f"{i}. {res['title']}\n   链接: {res['url']}\n   摘要: {res['snippet']}\n\n"
        
        return output

    def fetch_page(self, url):
        """
        [LOGIC]: 网页内容脱水提取捏。
        功能：抓取网页 HTML，剔除所有非文字类的“学术噪音”。
        """
        if self._is_blacklisted(url):
            return "权限警告：该域名已被大大列入黑名单，管家拒绝访问捏！"
            
        print(f"[Web] 📑 正在提取网页深度内容: {url}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(**self.browser_args)
                # 模拟真实学术访问身份捏
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
                page = context.new_page()
                
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
                content = page.content()
                browser.close()
                
                # [SCRAPING]: 使用 BeautifulSoup 进行脱水处理捏
                soup = BeautifulSoup(content, "html.parser")
                
                # 物理移除干扰标签（广告、页眉页脚等）
                for script_or_style in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    script_or_style.decompose()
                
                # [MEMORY PROTECT]: 仅保留纯净正文捏。
                raw_text = soup.get_text(separator="\n")
                lines = [line.strip() for line in raw_text.splitlines() if len(line.strip()) > 20]
                
                # [8GB VRAM ADAPTATION]: 
                # 严格物理截断正文长度，防止 8B 模型在 8GB 显存下因上下文爆表而 OOM 捏！
                clean_text = "\n".join(lines[:100]) 
                
                return f"【网页正文内容 - 来自 {url}】\n\n{clean_text}"
                
        except Exception as e:
            return f"错误：网页抓取失败捏。可能是由于对方设置了学术反爬。详情: {str(e)}"

    def execute(self, params):
        """
        [TOOL ENTRY]: 工具调度总入口，由 ModuleManager 调用捏。
        支持 'search' (学术搜索) 与 'browse' (内容提取) 双重指令。
        """
        action = params.get('action', 'search')
        
        if action == 'search' or 'query' in params:
            query = params.get('query') or params.get('Query')
            if not query:
                return "错误：搜索任务缺少 'query' 关键参数捏。"
            return self.search(query)
            
        elif action == 'browse' or 'url' in params:
            url = params.get('url') or params.get('URL')
            if not url:
                return "错误：浏览任务缺少 'url' 关键参数捏。"
            return self.fetch_page(url)
            
        else:
            return f"错误：浏览器还不支持 '{action}' 操作捏。请检查 JSON 指令捏！"

# =================================================================
# Copyright (c) 2026 lovesang. All Rights Reserved.
# [LOGIC]: 愿大大的科研之路永远没有噪音捏！🌸
# =================================================================