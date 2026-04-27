# -*- coding: utf-8 -*-
"""
test_check_cross_consistency.py · check_cross_consistency 回归测试

覆盖函数:
- parse_d_plus(text)
- parse_people(text)              ← 含 v2.0.1 团队上下文窗口过滤回归
- parse_money_in_yuan(text)
- check_duration_vs_dplus(...)    ★ happy path: case 8
- check_team_cost_vs_budget(...)  ★ happy path: case 11
- check_key_numbers_consistency(...) ★ happy path: case 12

测试目标:
    1. 解析函数的字符串边界(空格容错 / 边界数字 / 多匹配)
    2. v2.0.1 团队语境窗口过滤(培训规模 / 服务对象不计入团队成本)
    3. 三个 check_* 函数的失败 / 警告 / 通过 三态都能触发

运行:
    ./run_script.bat tests/test_check_cross_consistency.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_cross_consistency import (  # noqa: E402
    parse_d_plus,
    parse_people,
    parse_money_in_yuan,
    check_duration_vs_dplus,
    check_team_cost_vs_budget,
    check_key_numbers_consistency,
)


def assert_eq(actual, expected, label: str) -> bool:
    if actual == expected:
        print(f"  [PASS] {label}")
        return True
    print(f"  [FAIL] {label}")
    print(f"           expected: {expected!r}")
    print(f"           actual:   {actual!r}")
    return False


def assert_contains(issues: list[str], substring: str, label: str) -> bool:
    hit = any(substring in m for m in issues)
    if hit:
        print(f"  [PASS] {label}")
        return True
    print(f"  [FAIL] {label}")
    print(f"           expected substring: {substring!r}")
    print(f"           issues: {issues!r}")
    return False


def main() -> int:
    fails = 0
    cases = 0
    print("check_cross_consistency 测试")
    print()

    # ---- parse_d_plus ----
    cases += 1
    if not assert_eq(
        parse_d_plus("D+15 调研, D+30 初稿, D+60 终稿"),
        [15, 30, 60],
        "case_1_parse_d_plus_basic (happy path)",
    ):
        fails += 1

    cases += 1
    if not assert_eq(
        parse_d_plus("方案 D + 45,初稿 D+45"),
        [45, 45],
        "case_2_parse_d_plus_space_tolerant",
    ):
        fails += 1

    # ---- parse_people ----
    cases += 1
    if not assert_eq(
        parse_people("项目组共15人"),
        [15],
        "case_3_parse_people_team_context_hit",
    ):
        fails += 1

    cases += 1
    if not assert_eq(
        parse_people("培训不少于100人"),
        [],
        "case_4_parse_people_filter_training (v2.0.1 回归)",
    ):
        fails += 1

    cases += 1
    if not assert_eq(
        parse_people("服务3000万群众,项目组1人带技术骨干3位"),
        [1, 3],
        "case_5_parse_people_mixed_only_team",
    ):
        fails += 1

    # ---- parse_money_in_yuan ----
    cases += 1
    if not assert_eq(
        parse_money_in_yuan("预算50万元"),
        [(500000.0, "50万元")],
        "case_6_parse_money_wanyuan (happy path)",
    ):
        fails += 1

    cases += 1
    if not assert_eq(
        parse_money_in_yuan("保证金3000元"),
        [(3000.0, "3000元")],
        "case_7_parse_money_yuan_4digits",
    ):
        fails += 1

    # ---- check_duration_vs_dplus ----
    cases += 1
    if not assert_contains(
        check_duration_vs_dplus(60, [15, 30, 60]),
        "[通过]",
        "case_8_dplus_within_duration (happy path)",
    ):
        fails += 1

    cases += 1
    if not assert_contains(
        check_duration_vs_dplus(60, [130]),
        "[失败]",
        "case_9_dplus_hard_violation",
    ):
        fails += 1

    cases += 1
    if not assert_contains(
        check_duration_vs_dplus(60, [90]),
        "[警告]",
        "case_10_dplus_soft_violation",
    ):
        fails += 1

    # ---- check_team_cost_vs_budget ----
    cases += 1
    # 20人 × 50% × 60天 × 1500元 = 900000 元;预算 500000 × 1.5 = 750000 → 超
    if not assert_contains(
        check_team_cost_vs_budget(
            people_counts=[20],
            duration_days=60,
            budget_yuan=500_000,
            per_person_day_yuan=1500,
        ),
        "[失败]",
        "case_11_team_cost_overrun (happy path)",
    ):
        fails += 1

    # ---- check_key_numbers_consistency ----
    cases += 1
    # 预算 5,000,000 元;3000万元 = 30,000,000 在 1-10x 区间 → 警告
    if not assert_contains(
        check_key_numbers_consistency(
            "项目500万元,保险额3000万元",
            budget_yuan=5_000_000,
        ),
        "[警告]",
        "case_12_money_soft_inflated (happy path)",
    ):
        fails += 1

    print()
    print(f"总结:{cases - fails} 通过 / {fails} 失败  (共 {cases} 个 case)")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
