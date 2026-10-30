"""The bundled YC directory snapshot: its cards, read from the saved HTML page, and the companies a filter keeps."""

from __future__ import annotations

import html
import re
from functools import cache
from pathlib import Path
from urllib.parse import unquote

from contract import Card, Company, ExtractInput, ExtractOutput, ReadInput, ReadOutput, Season, SeasonFilter

SNAPSHOT = Path(__file__).parent / "data" / "yc_directory.html"
MAX_LIMIT = 20
FIRST_YEAR, LAST_YEAR = 2005, 2026
CARD = re.compile(
    r'<a class="[^"]*_company_\w+" href="https://www\.ycombinator\.com/companies/([^"]+)">(.*?)</div></div></div></a>',
    re.DOTALL,
)
NAME = re.compile(r'class="_coName_\w+">([^<]*)<')
LOCATION = re.compile(r'class="_coLocation_\w+">([^<]*)<')
TAGLINE = re.compile(r'<div class="mb-1\.5 text-sm"><span>([^<]*)</span>')
PILL = re.compile(r'companies\?(?:batch|industry)=([^"]+)"')
BATCH = re.compile(r"(Winter|Summer) (\d{4})")


def _one(pattern: re.Pattern[str], body: str, slug: str, what: str) -> str:
    found = pattern.findall(body)
    if len(found) != 1:
        raise ValueError(f"card {slug!r} has {len(found)} {what}s, not one")
    return html.unescape(found[0]).strip()


@cache
def cards() -> tuple[Card, ...]:
    """Every card of the snapshot, in page order."""
    found = CARD.findall(SNAPSHOT.read_text(encoding="utf-8"))
    if not found:
        raise ValueError(f"{SNAPSHOT.name} holds no company cards")
    return tuple(
        Card(
            position=position,
            slug=slug,
            name=_one(NAME, body, slug, "name"),
            location=_one(LOCATION, body, slug, "location"),
            tagline=_one(TAGLINE, body, slug, "tagline"),
            pills=[unquote(html.unescape(pill)) for pill in PILL.findall(body)],
        )
        for position, (slug, body) in enumerate(found)
    )


def read_directory(request: ReadInput, workspace: Path) -> ReadOutput:
    if request.offset < 0:
        raise ValueError("offset must be 0 or more")
    if not 1 <= request.limit <= MAX_LIMIT:
        raise ValueError(f"limit must be 1 to {MAX_LIMIT}")
    every = cards()
    return ReadOutput(total=len(every), offset=request.offset, cards=list(every[request.offset : request.offset + request.limit]))


def company(card: Card) -> Company:
    """A card as the record the task asks for."""
    batch = BATCH.fullmatch(card.pills[0]) if card.pills else None
    if batch is None or len(card.pills) < 2:
        raise ValueError(f"card {card.slug!r} does not start with a batch pill and an industry pill: {card.pills}")
    parts = [part.strip() for part in card.location.split(",")]
    return Company(
        slug=card.slug,
        name=card.name,
        season=Season(batch.group(1)),
        year=int(batch.group(2)),
        industry=card.pills[1],
        sub_industry=card.pills[2] if len(card.pills) > 2 else "",
        city=parts[0],
        country=parts[-1],
    )


def check_filter(task: ExtractInput) -> None:
    if not FIRST_YEAR <= task.year_from <= task.year_to <= LAST_YEAR:
        raise ValueError(f"years must satisfy {FIRST_YEAR} <= year_from <= year_to <= {LAST_YEAR}")
    if task.industry != task.industry.strip():
        raise ValueError("industry must not start or end with spaces")


def keeps(task: ExtractInput, record: Company) -> bool:
    return (
        (not task.industry or record.industry.casefold() == task.industry.casefold())
        and (task.season is SeasonFilter.ANY or record.season.value == task.season.value)
        and task.year_from <= record.year <= task.year_to
    )


def pin_matches(task: ExtractInput, workspace: Path) -> ExtractOutput:
    """The answer key: every card the filter keeps, read by code from the snapshot."""
    check_filter(task)
    kept = [record for record in map(company, cards()) if keeps(task, record)]
    return ExtractOutput(companies=kept, count=len(kept))
