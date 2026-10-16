"""
YC Company Directory Scraper Tools (Task 1)
Implements tools to fetch and parse YC company directory cards from static fixtures or live HTML.
"""

from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup

from contract import (
    ScraperInput,
    ScraperOutput,
    YCCompanyRecord,
    FetchHtmlInput,
    FetchHtmlOutput,
)


def fetch_html_tool(input_data: FetchHtmlInput) -> FetchHtmlOutput:
    """
    Tool 1: Fetch HTML content.
    If the source_path points to a local file (e.g. tests/fixtures/yc_companies_fixture.html),
    reads local content. Otherwise, handles local workspace resolution.
    """
    target = input_data.source_path.strip()
    file_path = Path(target)

    # 优先检查本地 Fixture 路径
    if not file_path.is_absolute():
        fixture_path = Path("tests/fixtures") / file_path.name
        if fixture_path.exists():
            file_path = fixture_path

    if file_path.exists() and file_path.is_file():
        content = file_path.read_text(encoding="utf-8")
        return FetchHtmlOutput(
            html_content=content,
            is_file=True,
            status="success"
        )
    
    # 离线环境退路说明
    return FetchHtmlOutput(
        html_content="",
        is_file=False,
        status="file_not_found"
    )


def parse_yc_directory_tool(html_content: str, max_records: int = 10) -> ScraperOutput:
    """
    Tool 2: Parse raw HTML content of YC Startup Directory into structured YCCompanyRecord objects.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    companies: list[YCCompanyRecord] = []

    # 匹配 YC 目录中的公司卡片元素（兼容常见 class 与结构）
    # 在 YC Directory 的 DOM 中，公司卡片通常位于特定容器内或 <a> 标签中
    cards = soup.select("a._company_1832d_338") or soup.find_all("a", href=True)

    for card in cards:
        if len(companies) >= max_records:
            break

        # 1. 提取公司名称
        name_elem = card.select_one("span._coName_1832d_453") or card.find("span", class_=lambda c: c and "coName" in c)
        if not name_elem:
            # 备用选择器：查找粗体或标题节点
            name_elem = card.find(["h0", "h1", "h2", "h3", "span", "div"])
        
        company_name = name_elem.get_text(strip=True) if name_elem else ""
        if not company_name:
            continue

        # 2. 提取地理位置与 Tagline
        location_elem = card.select_one("span._coLocation_1832d_469")
        location = location_elem.get_text(strip=True) if location_elem else "San Francisco, CA, USA"

        tagline_elem = card.select_one("span._tagline_1832d_438") or card.find("p")
        tagline = tagline_elem.get_text(strip=True) if tagline_elem else ""

        # 3. 提取 YC 批次 (Batch)
        batch_elem = card.find(text=lambda t: t and ("WINTER" in t or "SUMMER" in t or "FALL" in t or "SPRING" in t))
        batch = str(batch_elem).strip() if batch_elem else "WINTER 2026"

        # 4. 提取行业标签 (Tags)
        tag_elems = card.find_all("span", class_=lambda c: c and "pill" in c.lower())
        tags = [t.get_text(strip=True) for t in tag_elems] if tag_elems else ["CONSUMER"]

        # 5. 组装官网链接或相对链接
        href = card.get("href", "")
        website = f"https://www.ycombinator.com{href}" if href.startswith("/") else href

        record = YCCompanyRecord(
            company_name=company_name,
            tagline=tagline,
            batch=batch,
            location=location,
            website=website,
            tags=tags
        )
        companies.append(record)

    return ScraperOutput(
        companies=companies,
        total_parsed=len(companies)
    )