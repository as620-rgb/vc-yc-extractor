"""
YC Company Directory Scraper Verifier (Task 1)
Validates agent output against local static HTML fixture without LLM.
"""

from pathlib import Path
from typing import Any


def verify_task(task_input: Any, agent_output: Any, workspace_path: str) -> dict:
    """
    Standard entry function for nanoagent Harness invocations
    """
    constraints = []

    # 1. Safety check: Ensure the output structure exists and is of the correct type.
    has_companies = hasattr(agent_output, "companies") and isinstance(agent_output.companies, list)
    if not has_companies:
        return {
            "score": 0.0,
            "constraints": [{
                "id": "shape-check",
                "ok": False,
                "message": "agent_output missing 'companies' list field."
            }]
        }

    companies = agent_output.companies

    # ---- Constraint 1: Determination based on the number of companies ----
    ok_count = len(companies) >= 5 and len(companies) == getattr(agent_output, "total_parsed", len(companies))
    constraints.append({
        "id": "count-check",
        "ok": ok_count,
        "message": "" if ok_count else f"Expected at least 5 companies, got {len(companies)}"
    })

    # ---- Constraint 2: Assertion that core fields must not be null ----
    ok_fields = True
    for idx, co in enumerate(companies):
        if not (getattr(co, "company_name", None) and getattr(co, "batch", None)):
            ok_fields = False
            break
            
    constraints.append({
        "id": "field-completeness",
        "ok": ok_fields,
        "message": "" if ok_fields else "Missing company_name or batch in parsed records"
    })

    # ---- Constraint 3: Static Fixture – Accuracy Comparison for the First Company (DoorDash) ----
    ok_doordash = False
    if len(companies) > 0:
        first_co = companies[0]
        name_match = getattr(first_co, "company_name", "") == "DoorDash"
        batch_match = "2013" in str(getattr(first_co, "batch", ""))
        location_match = "San Francisco" in str(getattr(first_co, "location", ""))
        ok_doordash = name_match and batch_match and location_match

    constraints.append({
        "id": "doordash-exact-match",
        "ok": ok_doordash,
        "message": "" if ok_doordash else "DoorDash data mismatch (check name, location, or batch)"
    })

    # ---- Constraint 4: Accuracy Comparison for the Second Company (Airbnb) Using Static Fixtures ----
    ok_airbnb = False
    if len(companies) > 1:
        second_co = companies[1]
        name_match = getattr(second_co, "company_name", "") == "Airbnb"
        batch_match = "2009" in str(getattr(second_co, "batch", ""))
        ok_airbnb = name_match and batch_match

    constraints.append({
        "id": "airbnb-exact-match",
        "ok": ok_airbnb,
        "message": "" if ok_airbnb else "Airbnb data mismatch (check name or batch)"
    })

    # Calculate the final score (1.0 if all constraints are met, otherwise 0.0).
    all_ok = all(c["ok"] for c in constraints)
    score = 1.0 if all_ok else 0.0

    return {
        "score": score,
        "constraints": constraints
    }
