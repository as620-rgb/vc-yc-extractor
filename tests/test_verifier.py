"""
Offline Verifier Test for YC Scraper Task
"""

from types import SimpleNamespace
from verifier.task import verify_task


def test_verify_task_gold():
    """Test whether the Verifier assigns a perfect score of 1.0 when the Agent extracts the correct data."""
    # Output Structure of a Successful Agent (Gold Standard Case)
    mock_agent_output = SimpleNamespace(
        companies=[
            SimpleNamespace(
                company_name="DoorDash",
                batch="SUMMER 2013",
                location="San Francisco, CA, USA",
                website="https://www.ycombinator.com/companies/doordash",
            ),
            SimpleNamespace(
                company_name="Airbnb",
                batch="WINTER 2009",
                location="San Francisco, CA, USA",
                website="https://www.ycombinator.com/companies/airbnb",
            ),
            SimpleNamespace(
                company_name="Coinbase",
                batch="SUMMER 2012",
                location="Los Angeles, CA, USA",
                website="https://www.ycombinator.com/companies/coinbase",
            ),
            SimpleNamespace(
                company_name="Groww",
                batch="WINTER 2018",
                location="Bengaluru, KA, India",
                website="https://www.ycombinator.com/companies/groww",
            ),
            SimpleNamespace(
                company_name="Instacart",
                batch="SUMMER 2012",
                location="San Francisco, CA, USA",
                website="https://www.ycombinator.com/companies/instacart",
            ),
        ],
        total_parsed=5,
    )

    # Run Verifier check
    result = verify_task(
        task_input={}, agent_output=mock_agent_output, workspace_path="."
    )

    # Assertion Verdict Result
    assert result["score"] == 1.0
    assert all(c["ok"] for c in result["constraints"])


def test_verify_task_broken():
    """Test whether the Verifier accurately captures failed rules when the Agent extracts incorrect data."""
    mock_broken_output = SimpleNamespace(
        companies=[
            SimpleNamespace(
                company_name="WrongName",  # Intentionally providing an incorrect name
                batch="WINTER 2026",
                location="Unknown",
                website="",
            )
        ],
        total_parsed=1,
    )

    result = verify_task(
        task_input={}, agent_output=mock_broken_output, workspace_path="."
    )

    # Assertion failed
    assert result["score"] == 0.0
