# -*- coding: utf-8 -*-
"""
test_parse_tender.py · parse_tender 回归测试

覆盖函数:
- normalize_text(text)
- extract_raw_lines_with_features(text)  ★ happy path: case 3
- extract_section_by_anchors(text, anchors)  ★ happy path: case 6
- extract_substantial_marks(text)  ★ happy path: case 7
- extract_score_items_raw_positions(text, anchors)  ★ happy path: case 9

测试目标:
    1. 文本预处理:多空白压缩 + 多换行压缩
    2. 行特征:is_standalone / has_chapter_num / has_dots_leader 三类标签
    3. 章节切片按 anchors 切
    4. ★▲ 标记抽取
    5. 评审办法范围内按 (N分) 切位置

运行:
    ./run_script.bat tests/test_parse_tender.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from parse_tender import (  # noqa: E402
    normalize_text,
    extract_raw_lines_with_features,
    extract_section_by_anchors,
    extract_substantial_marks,
    extract_score_items_raw_positions,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "parse_tender"


def main() -> int:
    fails = 0
    cases = 0
    print("parse_tender 测试")
    print()

    # ---- case 1: normalize_text 多空白压缩 ----
    cases += 1
    actual = normalize_text("测试   多  空格")
    expected = "测试 多 空格"
    ok = actual == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] case_1_normalize_collapse_spaces")
    if not ok:
        print(f"           expected: {expected!r}")
        print(f"           actual:   {actual!r}")
        fails += 1

    # ---- case 2: normalize_text 多换行压缩 ----
    cases += 1
    actual = normalize_text("行1\n\n\n\n行2")
    expected = "行1\n\n行2"
    ok = actual == expected
    print(f"  [{'PASS' if ok else 'FAIL'}] case_2_normalize_collapse_newlines")
    if not ok:
        print(f"           expected: {expected!r}")
        print(f"           actual:   {actual!r}")
        fails += 1

    # ---- case 3: extract_raw_lines_with_features 短行 vs 长行 (happy path)----
    cases += 1
    text = "短行\n这是一个长度刻意超过六十个字符的长行,目的是验证 is_standalone 在超长行上的反向判定逻辑确实生效不会被误判为短独立行,需要超过六十"
    rows = extract_raw_lines_with_features(text)
    ok = (
        len(rows) == 2
        and rows[0]["is_standalone"] is True
        and rows[0]["text"] == "短行"
        and rows[1]["is_standalone"] is False
        and rows[1]["length"] > 60
    )
    print(f"  [{'PASS' if ok else 'FAIL'}] case_3_features_standalone (happy path)")
    if not ok:
        print(f"           rows: {rows}")
        fails += 1

    # ---- case 4: has_chapter_num ----
    cases += 1
    rows = extract_raw_lines_with_features("第三章 评审办法")
    ok = len(rows) == 1 and rows[0]["has_chapter_num"] is True
    print(f"  [{'PASS' if ok else 'FAIL'}] case_4_features_chapter_num")
    if not ok:
        print(f"           rows: {rows}")
        fails += 1

    # ---- case 5: has_dots_leader ----
    cases += 1
    rows = extract_raw_lines_with_features("目录...........5")
    ok = len(rows) == 1 and rows[0]["has_dots_leader"] is True
    print(f"  [{'PASS' if ok else 'FAIL'}] case_5_features_dots_leader")
    if not ok:
        print(f"           rows: {rows}")
        fails += 1

    # ---- case 6: extract_section_by_anchors (happy path)----
    cases += 1
    text = "L0\nL1\nL2\nL3\nL4\nL5\nL6\nL7\nL8\nL9"
    anchors = [{"section": "评审办法", "start_line": 5, "end_line": 10}]
    sections = extract_section_by_anchors(text, anchors)
    ok = (
        "评审办法" in sections
        and sections["评审办法"]["start"] == 5
        and sections["评审办法"]["end"] == 10
        and sections["评审办法"]["content"] == "L5\nL6\nL7\nL8\nL9"
    )
    print(f"  [{'PASS' if ok else 'FAIL'}] case_6_section_by_anchors_slice (happy path)")
    if not ok:
        print(f"           sections: {sections}")
        fails += 1

    # ---- case 7: extract_substantial_marks 从 fixture 文件 (happy path)----
    cases += 1
    with_marks_text = (FIXTURES / "with_marks.txt").read_text(encoding="utf-8")
    marks = extract_substantial_marks(with_marks_text)
    line_nos = [m["line_no"] for m in marks]
    ok = (
        len(marks) == 4
        and line_nos == sorted(line_nos)  # 单调递增
        and all(("★" in m["text"]) or ("▲" in m["text"]) for m in marks)
    )
    print(f"  [{'PASS' if ok else 'FAIL'}] case_7_substantial_marks_from_fixture (happy path)")
    if not ok:
        print(f"           marks: {marks}")
        fails += 1

    # ---- case 8: extract_substantial_marks 边界(无标记)----
    cases += 1
    marks = extract_substantial_marks("纯文本无任何标记符号")
    ok = marks == []
    print(f"  [{'PASS' if ok else 'FAIL'}] case_8_substantial_marks_empty")
    if not ok:
        print(f"           marks: {marks}")
        fails += 1

    # ---- case 9: extract_score_items_raw_positions (happy path)----
    cases += 1
    score_text = (
        "第三章 评审办法\n"
        "\n"
        "(20分)项目管理体系\n"
        "评审依据:制度文件\n"
        "\n"
        "(15分)技术方案\n"
        "评审依据:架构图\n"
    )
    # lines[0..7]; 评审办法范围 0..7;match 在 line 2 和 line 5
    score_anchors = [{"section": "评审办法", "start_line": 0, "end_line": 7}]
    positions = extract_score_items_raw_positions(score_text, score_anchors)
    ok = (
        len(positions) == 2
        and positions[0]["start_line"] == 2
        and positions[1]["start_line"] == 5
        and "(20分)" in positions[0]["raw_text"]
        and "(15分)" in positions[1]["raw_text"]
    )
    print(f"  [{'PASS' if ok else 'FAIL'}] case_9_score_items_raw_positions (happy path)")
    if not ok:
        print(f"           positions: {positions}")
        fails += 1

    # ---- case 10: extract_score_items_raw_positions 缺评审办法 anchor ----
    cases += 1
    positions = extract_score_items_raw_positions("无关文本", [])
    ok = positions == []
    print(f"  [{'PASS' if ok else 'FAIL'}] case_10_score_items_no_anchor_fallback")
    if not ok:
        print(f"           positions: {positions}")
        fails += 1

    print()
    print(f"总结:{cases - fails} 通过 / {fails} 失败  (共 {cases} 个 case)")
    return 1 if fails > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
