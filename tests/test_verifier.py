from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import ExtractInput, ExtractOutput, ReadInput, ReadOutput
from plugin.directory import pin_matches, read_directory

FINTECH = {"industry": "Fintech", "season": "any", "year_from": 2005, "year_to": 2026}


def task(**changes) -> ExtractInput:
    return build_output({**FINTECH, **changes}, ExtractInput)


def key(given: ExtractInput, workspace: Path) -> ExtractOutput:
    # Values reach the verifier as NanoAgent's sandbox builds them: from JSON into contract classes.
    return build_output(plain_output(pin_matches(given, workspace)), ExtractOutput)


def submit(companies: list[dict], count: int | None = None) -> ExtractOutput:
    return build_output({"companies": companies, "count": len(companies) if count is None else count}, ExtractOutput)


def check(given: ExtractInput, output: ExtractOutput, workspace: Path) -> dict:
    return verifier.verify_task("extract-companies", given, output, key(given, workspace), str(workspace))


def failing(verdict: dict) -> list[str]:
    return [entry["id"] for entry in verdict["details"]["constraints"] if not entry["ok"]]


def test_the_snapshot_parses_into_known_cards(tmp_path: Path) -> None:
    every = key(task(industry=""), tmp_path)
    assert every.count == 40
    first = plain_output(every.companies[0])
    assert first == {
        "slug": "doordash", "name": "DoorDash", "season": "Summer", "year": 2013, "industry": "Consumer",
        "sub_industry": "Food and Beverage", "city": "San Francisco", "country": "USA",
    }
    benchling = next(c for c in every.companies if c.slug == "benchling")
    assert benchling.sub_industry == ""  # a card with one industry pill


def test_approves_the_correct_answer(tmp_path: Path) -> None:
    given = task()
    answer = key(given, tmp_path)
    assert [c.slug for c in answer.companies] == ["coinbase", "groww", "truebill", "brex", "sendwave"]
    verdict = check(given, answer, tmp_path)
    assert verdict["valid"] is True and verdict["score"] == 1.0


def test_industry_matches_ignoring_case_and_never_the_sub_industry(tmp_path: Path) -> None:
    assert key(task(industry="fintech"), tmp_path).count == 5
    assert key(task(industry="Analytics"), tmp_path).count == 0  # Analytics is only ever a sub-industry


def test_year_bounds_are_inclusive(tmp_path: Path) -> None:
    answer = key(task(year_from=2012, year_to=2012), tmp_path)
    assert [c.slug for c in answer.companies] == ["coinbase", "sendwave"]
    assert key(task(year_from=2013, year_to=2016), tmp_path).count == 1  # truebill, Winter 2016


def test_season_filter(tmp_path: Path) -> None:
    answer = key(task(season="Winter"), tmp_path)
    assert [c.slug for c in answer.companies] == ["groww", "truebill", "brex", "sendwave"]


def test_an_empty_answer_is_correct_when_nothing_matches(tmp_path: Path) -> None:
    given = task(industry="Space Mining")
    assert check(given, submit([]), tmp_path)["valid"] is True
    assert check(given, submit([], count=1), tmp_path)["valid"] is False


def test_rejects_a_missing_company(tmp_path: Path) -> None:
    given = task()
    rows = plain_output(key(given, tmp_path))["companies"][:-1]
    verdict = check(given, submit(rows), tmp_path)
    assert verdict["valid"] is False and failing(verdict) == ["no-missing"]
    assert "sendwave" in verdict["message"]


def test_rejects_an_extra_company(tmp_path: Path) -> None:
    given = task()
    rows = plain_output(key(given, tmp_path))["companies"]
    airbnb = plain_output(key(task(industry="Consumer", year_from=2009, year_to=2009), tmp_path))["companies"]
    verdict = check(given, submit(rows + airbnb), tmp_path)
    assert verdict["valid"] is False and set(failing(verdict)) == {"within-filter", "no-extra"}


def test_rejects_a_fabricated_company(tmp_path: Path) -> None:
    given = task()
    rows = plain_output(key(given, tmp_path))["companies"]
    fake = {**rows[0], "slug": "fakepay", "name": "FakePay"}
    verdict = check(given, submit(rows + [fake]), tmp_path)
    assert failing(verdict) == ["no-extra"]


def test_rejects_a_wrong_field(tmp_path: Path) -> None:
    given = task()
    rows = plain_output(key(given, tmp_path))["companies"]
    rows[1] = {**rows[1], "city": "Bengaluru, KA"}
    verdict = check(given, submit(rows), tmp_path)
    assert failing(verdict) == ["fields-exact"] and "groww.city" in verdict["message"]


def test_rejects_a_record_whose_year_breaks_the_filter(tmp_path: Path) -> None:
    given = task(year_from=2012, year_to=2012)
    rows = plain_output(key(given, tmp_path))["companies"]
    rows[0] = {**rows[0], "year": 2013}
    assert set(failing(check(given, submit(rows), tmp_path))) == {"within-filter", "fields-exact"}


def test_rejects_duplicates_and_wrong_order(tmp_path: Path) -> None:
    given = task()
    rows = plain_output(key(given, tmp_path))["companies"]
    assert "no-duplicates" in failing(check(given, submit(rows + rows[:1]), tmp_path))
    assert failing(check(given, submit(list(reversed(rows))), tmp_path)) == ["directory-order"]


def test_rejects_an_impossible_filter(tmp_path: Path) -> None:
    bad = task(year_from=2020, year_to=2010)
    assert verifier.verify_input("pin_matches", bad)["valid"] is False
    assert verifier.verify_task("extract-companies", bad, submit([]), None, str(tmp_path))["valid"] is False
    with pytest.raises(ValueError, match="year_from"):
        pin_matches(bad, tmp_path)
    assert verifier.verify_input("pin_matches", task(industry=" Fintech"))["valid"] is False


def test_rejects_a_task_with_no_answer_key(tmp_path: Path) -> None:
    assert verifier.verify_task("extract-companies", task(), submit([]), None, str(tmp_path))["valid"] is False


def test_read_directory_pages_and_its_checks(tmp_path: Path) -> None:
    given = build_output({"offset": 30, "limit": 20}, ReadInput)
    page = build_output(plain_output(read_directory(given, tmp_path)), ReadOutput)
    assert page.total == 40 and [c.position for c in page.cards] == list(range(30, 40))
    assert verifier.verify_output("read_directory", given, page, str(tmp_path))["valid"] is True
    past = build_output({"offset": 45, "limit": 5}, ReadInput)
    assert read_directory(past, tmp_path).cards == []
    shifted = build_output({**plain_output(page), "cards": plain_output(page)["cards"][1:]}, ReadOutput)
    assert verifier.verify_output("read_directory", given, shifted, str(tmp_path))["valid"] is False
    for bad in ({"offset": 0, "limit": 0}, {"offset": 0, "limit": 21}, {"offset": -1, "limit": 5}):
        assert verifier.verify_input("read_directory", build_output(bad, ReadInput))["valid"] is False
        with pytest.raises(ValueError):
            read_directory(build_output(bad, ReadInput), tmp_path)
