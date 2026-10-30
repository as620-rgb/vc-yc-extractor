"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_DIRECTORY = "read_directory"
    PIN_MATCHES = "pin_matches"


class Task(Enum):
    EXTRACT_COMPANIES = "extract-companies"


class Season(Enum):
    WINTER = "Winter"
    SUMMER = "Summer"


class SeasonFilter(Enum):
    ANY = "any"
    WINTER = "Winter"
    SUMMER = "Summer"


INDUSTRY = (
    "A top-level industry exactly as the directory names it (compared ignoring case), e.g. Fintech or B2B; "
    "empty for every industry"
)
SLUG = "The company's directory slug, the last part of its card link, e.g. rigetti-computing"


@dataclass
class ExtractInput(Output):
    industry: Annotated[str, INDUSTRY]
    season: Annotated[SeasonFilter, "any, Winter or Summer: the season of the YC batch to keep"]
    year_from: Annotated[int, "The first batch year to keep, inclusive, 2005 to 2026"]
    year_to: Annotated[int, "The last batch year to keep, inclusive, from year_from to 2026"]


@dataclass
class Company(Output):
    slug: Annotated[str, SLUG]
    name: Annotated[str, "The company's name exactly as its card shows it"]
    season: Annotated[Season, "The season of its batch pill, e.g. Summer for Summer 2013"]
    year: Annotated[int, "The year of its batch pill, e.g. 2013 for Summer 2013"]
    industry: Annotated[str, "The first industry pill after the batch pill, e.g. Consumer"]
    sub_industry: Annotated[str, "The second industry pill, e.g. Food and Beverage; empty when the card has only one"]
    city: Annotated[str, "The location's text before its first comma, e.g. San Francisco"]
    country: Annotated[str, "The location's text after its last comma, e.g. USA"]


@dataclass
class ExtractOutput(Output):
    companies: Annotated[list[Company], "Every company that matches the filter, in directory order; [] for none"]
    count: Annotated[int, "How many companies match"]


@dataclass
class ReadInput(Output):
    offset: Annotated[int, "The position of the first card to read, from 0"]
    limit: Annotated[int, "How many cards to read, 1 to 20"]


@dataclass
class Card(Output):
    position: Annotated[int, "The card's position in the directory, from 0"]
    slug: Annotated[str, SLUG]
    name: Annotated[str, "The name shown on the card"]
    location: Annotated[str, 'The location shown on the card, e.g. "San Francisco, CA, USA"']
    tagline: Annotated[str, "The card's one-line description"]
    pills: Annotated[list[str], 'The card\'s pills in order: its batch first, then its industries, e.g. ["Summer 2013", "Consumer"]']


@dataclass
class ReadOutput(Output):
    total: Annotated[int, "How many cards the directory snapshot holds"]
    offset: Annotated[int, "The offset read from"]
    cards: Annotated[list[Card], "The cards from offset on, at most limit of them; [] past the end"]


TOOLS = {
    Tool.READ_DIRECTORY: (ReadInput, ReadOutput),
    Tool.PIN_MATCHES: (ExtractInput, ExtractOutput),
}
TASKS = {Task.EXTRACT_COMPANIES: (ExtractInput, ExtractOutput)}
