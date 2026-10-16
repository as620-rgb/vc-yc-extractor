"""
Offline Verifier Test for YC Scraper Task
"""

from types import SimpleNamespace
from verifier.task import verify_task


def test_verify_task_gold():
    """测试当 Agent 提取出正确数据时，Verifier 是否给出 1.0 满分"""
    # 模拟成功的 Agent 输出结构 (Gold Standard Case)
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

    # 运行 Verifier 校验
    result = verify_task(
        task_input={}, agent_output=mock_agent_output, workspace_path="."
    )

    # 断言 Verdict 结果
    assert result["score"] == 1.0
    assert all(c["ok"] for c in result["constraints"])


def test_verify_task_broken():
    """测试当 Agent 提取错误数据时，Verifier 是否准确捕获失败规则"""
    mock_broken_output = SimpleNamespace(
        companies=[
            SimpleNamespace(
                company_name="WrongName",  # 故意给出错误名字
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

    # 断言失败
    assert result["score"] == 0.0