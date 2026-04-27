# -*- coding: utf-8 -*-
"""
test_compliance_check.py · compliance_check 回归测试

覆盖函数:
- normalize_for_match(text)
- extract_candidates(row)
- check_coverage(docx_text, matrix, mode_map)  ★ happy path: case 3
- check_substantial_response(docx_text, matrix)  ★ happy path: case 6
- check_template_residues(docx_text)
- check_font_safety(docx_path)  ★ happy path: case 8

测试目标:
    1. 漏答检测(check_coverage missing)
    2. 弱覆盖判定(out_of_scope mode_map 跳过)
    3. 模板残留扫描
    4. ★实质性响应近邻关联
    5. 字体安全(MS Mincho 等非白名单 eastAsia 触发)

运行:
    ./run_script.bat tests/test_compliance_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from compliance_check import (  # noqa: E402
    normalize_for_match,
    extract_candidates,
    check_coverage,
    check_substantial_response,
    check_template_residues,
    check_font_safety,
    load_matrix,
    read_docx_text,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "compliance_check"
MATRIX_CSV = FIXTURES / "scoring_matrix_minimal.csv"
CLEAN_DOCX = FIXTURES / "clean_response.docx"
MISSING_DOCX = FIXTURES / "missing_keywords.docx"
FONT_UNSAFE_DOCX = FIXTURES / "font_unsafe.docx"


def main() -> int:
    fails = 0
    cases = 0
    print("compliance_check 测试")
    print()

    matrix = load_matrix(MATRIX_CSV)

    # ---- case 1: normalize_for_match ----
    cases += 1
    actual = normalize_for_match("中文 含 空格,标点;括号(测试)!")
    # 空格 / 中英标点 / 括号都被 strip,但叹号"!"不在 NORMALIZE_PATTERN
    expected_contains = "中文含空格标点括号测试"
    ok = expected_contains in actual
    print(f"  [{'PASS' if ok else 'FAIL'}] case_1_normalize_for_match")
    if not ok:
        print(f"           actual={actual!r}, expected to contain {expected_contains!r}")
        fails += 1

    # ---- case 2: extract_candidates ----
    cases += 1
    row = {"评分项": "项目管理体系", "关键词": "PMBOK;敏捷"}
    cand = extract_candidates(row)
    ok = "项目管理体系" in cand and "PMBOK" in cand and "敏捷" in cand
    print(f"  [{'PASS' if ok else 'FAIL'}] case_2_extract_candidates")
    if not ok:
        print(f"           cand={cand}")
        fails += 1

    # ---- case 3: check_coverage on clean docx (happy path)----
    cases += 1
    text, _ = read_docx_text(CLEAN_DOCX)
    results = check_coverage(text, matrix, mode_map=None)
    statuses = [r["status"] for r in results]
    ok = all(s == "covered" for s in statuses) and len(results) == 2
    print(f"  [{'PASS' if ok else 'FAIL'}] case_3_clean_all_covered (happy path)")
    if not ok:
        print(f"           statuses={statuses}")
        for r in results:
            print(f"           - {r}")
        fails += 1

    # ---- case 4: check_coverage on missing_keywords docx ----
    cases += 1
    text_missing, _ = read_docx_text(MISSING_DOCX)
    results = check_coverage(text_missing, matrix, mode_map=None)
    statuses = [r["status"] for r in results]
    ok = "missing" in statuses or "partial" in statuses
    print(f"  [{'PASS' if ok else 'FAIL'}] case_4_missing_detected")
    if not ok:
        print(f"           statuses={statuses}")
        fails += 1

    # ---- case 5: mode_map 把评分项归属 → out_of_scope ----
    cases += 1
    results = check_coverage(text, matrix, mode_map={"技术方案": "B"})
    statuses = [r["status"] for r in results]
    ok = all(s == "out_of_scope" for s in statuses)
    print(f"  [{'PASS' if ok else 'FAIL'}] case_5_mode_map_skip")
    if not ok:
        print(f"           statuses={statuses}")
        fails += 1

    # ---- case 6: check_substantial_response (happy path)----
    cases += 1
    # 文本含 ★关键词 + "完全满足" 在近邻
    test_text = "技术方案完整性是核心要素,本部分内容完全满足★实质性响应条款的所有要求。"
    results = check_substantial_response(test_text, matrix)
    ok = any(r.get("responded") for r in results)
    print(f"  [{'PASS' if ok else 'FAIL'}] case_6_substantial_responded (happy path)")
    if not ok:
        print(f"           results={results}")
        fails += 1

    # ---- case 7: check_template_residues 检测占位符 ----
    cases += 1
    residues = check_template_residues("尊敬的[投标人名称]您好,请补充 TODO 项")
    ok = len(residues) >= 2  # [投标人名称] + TODO 各 1 处
    print(f"  [{'PASS' if ok else 'FAIL'}] case_7_template_residues")
    if not ok:
        print(f"           residues={residues}")
        fails += 1

    # ---- case 8: check_font_safety on font_unsafe.docx (happy path)----
    cases += 1
    issues = check_font_safety(FONT_UNSAFE_DOCX)
    ok = any("MS Mincho" in m for m in issues)
    print(f"  [{'PASS' if ok else 'FAIL'}] case_8_font_unsafe_detected (happy path)")
    if not ok:
        print(f"           issues={issues}")
        fails += 1

    # ---- 附加 case: clean docx 字体安全应通过 ----
    cases += 1
    issues_clean = check_font_safety(CLEAN_DOCX)
    ok = len(issues_clean) == 0
    print(f"  [{'PASS' if ok else 'FAIL'}] case_9_clean_font_safety_passes")
    if not ok:
        print(f"           clean docx issues={issues_clean}")
        fails += 1

    print()
    print(f"总结:{cases - fails} 通过 / {fails} 失败  (共 {cases} 个 case)")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
