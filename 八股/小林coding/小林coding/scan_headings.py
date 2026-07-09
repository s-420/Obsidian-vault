#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan all markdown files and detect section vs question headings."""

import re
import os

MD_DIR = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\md_output"
OUTPUT = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\headings_analysis.txt"

KNOWN_SECTIONS = {
    "2.Java基础面试篇.md": [
        "概念", "数据类型", "面向对象", "关键字",
        "深拷贝和浅拷贝", "泛型", "对象", "反射", "注解",
        "异常", "object", "Java 新特性", "序列化",
        "设计模式", "I/O", "其他"
    ],
}

results = []

for fname in sorted(os.listdir(MD_DIR)):
    if not fname.endswith(".md"):
        continue
    
    path = os.path.join(MD_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Remove front matter
    text = re.sub(r'^---.*?---\s*', "", text, flags=re.DOTALL).strip()
    
    # Find all # headings
    headings = re.findall(r'^# (.+)$', text, re.MULTILINE)
    
    results.append(f"=== {fname} ({len(headings)} headings) ===")
    
    # Detect potential section headers (short names, not questions)
    potential_sections = []
    potential_questions = []
    
    if fname in KNOWN_SECTIONS:
        # Use known sections, mark remaining as questions
        known = KNOWN_SECTIONS[fname]
        for h in headings:
            if h in known:
                potential_sections.append(h)
            else:
                potential_questions.append(h)
    else:
        # Auto-detect: sections are short (<=6 chars typically) and don't end with ?
        for h in headings:
            h_stripped = h.strip()
            # Heuristics for section header:
            # 1. Short (Chinese: 2-4 chars typically)
            # 2. Doesn't end with ?/?/？/吗/呢
            # 3. No punctuation marks typical of questions
            is_question = (
                h_stripped.endswith("?") or
                h_stripped.endswith("？") or
                h_stripped.endswith("吗") or
                h_stripped.endswith("呢") or
                h_stripped.endswith("么") or
                h_stripped.endswith("的") or
                len(h_stripped) > 10 or
                "什么" in h_stripped or
                "如何" in h_stripped or
                "怎么" in h_stripped or
                "哪些" in h_stripped or
                "为什么" in h_stripped
            )
            
            if not is_question and len(h_stripped) <= 8:
                potential_sections.append(h_stripped)
            else:
                potential_questions.append(h_stripped)
    
    results.append(f"  Potential sections ({len(potential_sections)}):")
    for s in potential_sections:
        results.append(f"    - '{s}'")
    results.append(f"  Potential questions ({len(potential_questions)}):")
    for q in potential_questions:
        results.append(f"    - '{q[:50]}'" + ("..." if len(q) > 50 else ""))
    results.append("")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print(f"Analysis written to {OUTPUT}")
