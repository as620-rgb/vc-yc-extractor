from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Optional
from slimconfig import Output

class Tool(Enum):
    FETCH_HTML = "fetch_html"
    PARSE_YC_CARD = "parse_yc_card"

class Task(Enum):
    YC_SCRAPER = "yc-scraper"

@dataclass
class ScraperInput(Output):
    target_url_or_file: Annotated[str, "URL or local HTML file path for a YC batch directory"]
    max_records: Annotated[int, "Limit of companies to extract"] = 10

@dataclass
class YCCompanyRecord(Output):
    company_name: str
    tagline: str
    batch: str  # 例如 "W24"
    location: Optional[str]
    website: str

@dataclass
class ScraperOutput(Output):
    companies: list[YCCompanyRecord]
    total_parsed: int

@dataclass
class FetchHtmlInput(Output):
    source_path: Annotated[str, "Local fixture path or HTML file name"]

@dataclass
class FetchHtmlOutput(Output):
    html_content: str
    is_file: bool
    status: str

TOOLS = {
    Tool.FETCH_HTML: (FetchHtmlInput, FetchHtmlOutput),
}