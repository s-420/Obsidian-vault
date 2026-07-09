#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse Java基础面试篇.md and generate XMind mind map file."""

import re
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape
import os
import uuid

# ======== Configuration ========
MD_FILE = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\md_output\2.Java基础面试篇.md"
OUTPUT_DIR = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\mindmap"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Java基础面试篇.xmind")

# Known section headers in the file
SECTION_HEADERS = [
    "概念", "数据类型", "面向对象", "关键字",
    "深拷贝和浅拷贝", "泛型", "对象", "反射", "注解",
    "异常", "object", "Java 新特性", "序列化",
    "设计模式", "I/O", "其他"
]

# Sections that go under 数据结构 (all others go under 概念)
DATA_STRUCTURE_SECTIONS = ["数据类型"]


def generate_id():
    return "id-" + str(uuid.uuid4()).replace("-", "")


def parse_markdown(filepath):
    """Parse markdown file and extract structure: sections, questions, answers."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Remove front matter
    content_lines = []
    in_front_matter = False
    skipped_front_matter = False
    for line in lines:
        if line.strip() == "---" and not in_front_matter:
            in_front_matter = True
            skipped_front_matter = True
            continue
        if line.strip() == "---" and in_front_matter and skipped_front_matter:
            in_front_matter = False
            continue
        if not in_front_matter:
            content_lines.append(line)

    text = "".join(content_lines)

    # Split by headings
    # Pattern: # heading
    pattern = re.compile(r'^# (.+)$', re.MULTILINE)
    parts = pattern.split(text)

    # parts[0] is content before first heading (usually empty)
    # Then alternating: heading text, content, heading text, content, ...
    # But we need to handle the title heading

    # Structure to hold parsed data
    # We'll build a list of (type, title, content) tuples
    # type: "section" | "question" | "title"

    nodes = []
    current_section = None  # Track which section we're in
    # Map: section_name -> list of (question_text, answer_text)
    section_data = {}  # Also for questions directly under main
    standalone_questions = []  # Questions not under any subsection

    # Known sections for tracking
    known_sections = set(SECTION_HEADERS)

    # Process heading-content pairs
    i = 1
    while i < len(parts):
        heading = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        i += 2

        # Skip main title
        if heading == "Java基础面试题":
            continue

        # Check if it's a known section header
        if heading in known_sections:
            current_section = heading
            section_data[heading] = []
            continue

        # Otherwise it's a question
        question = heading
        answer = content

        if current_section:
            section_data.setdefault(current_section, []).append((question, answer))
        else:
            standalone_questions.append((question, answer))

    return section_data, standalone_questions


def build_xmind_xml(section_data, standalone_questions):
    """Build the XMind content.xml as a string."""
    # Generate IDs
    root_id = generate_id()
    concept_id = generate_id()
    ds_id = generate_id()

    # Build XML structure manually (more control)
    xml_parts = []

    # XML declaration + root element
    xml_parts.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    xml_parts.append('<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink">')
    xml_parts.append(f'  <sheet id="sheet-{generate_id()}">')

    # Root topic: Java基础
    xml_parts.append(f'    <topic id="{root_id}">')
    xml_parts.append('      <title>Java基础</title>')
    xml_parts.append('      <children>')
    xml_parts.append('        <topics type="attached">')

    # ===== Subtopic 1: 概念 =====
    xml_parts.append(f'          <topic id="{concept_id}">')
    xml_parts.append('            <title>概念</title>')
    xml_parts.append('            <children>')
    xml_parts.append('              <topics type="attached">')

    # Known subsections to include under 概念
    concept_sub_sections = [
        "面向对象", "关键字", "深拷贝和浅拷贝", "泛型",
        "对象", "反射", "注解", "异常", "object",
        "Java 新特性", "序列化", "设计模式", "I/O", "其他"
    ]

    # First, add standalone questions (under 概念 section but before any subsection)
    for q_text, a_text in standalone_questions:
        q_id = generate_id()
        xml_parts.append(f'                <topic id="{q_id}">')
        xml_parts.append(f'                  <title>{escape(q_text)}</title>')
        # Add answer as notes
        if a_text:
            safe_answer = escape(a_text)
            # Convert newlines to <br/> for HTML note
            safe_answer_html = safe_answer.replace("\n", "<br/>")
            xml_parts.append('                  <notes>')
            xml_parts.append('                    <html>')
            xml_parts.append('                      <head/>')
            xml_parts.append(f'                        <body>{safe_answer_html}</body>')
            xml_parts.append('                    </html>')
            xml_parts.append('                  </notes>')
        xml_parts.append(f'                </topic>')

    # Add concept subsections with their questions
    for sub_name in concept_sub_sections:
        if sub_name in section_data and section_data[sub_name]:
            sub_id = generate_id()
            xml_parts.append(f'                <topic id="{sub_id}">')
            xml_parts.append(f'                  <title>{escape(sub_name)}</title>')
            xml_parts.append('                  <children>')
            xml_parts.append('                    <topics type="attached">')

            for q_text, a_text in section_data[sub_name]:
                q_id = generate_id()
                xml_parts.append(f'                      <topic id="{q_id}">')
                xml_parts.append(f'                        <title>{escape(q_text)}</title>')
                if a_text:
                    safe_answer = escape(a_text)
                    safe_answer_html = safe_answer.replace("\n", "<br/>")
                    xml_parts.append('                        <notes>')
                    xml_parts.append('                          <html>')
                    xml_parts.append('                            <head/>')
                    xml_parts.append(f'                              <body>{safe_answer_html}</body>')
                    xml_parts.append('                          </html>')
                    xml_parts.append('                        </notes>')
                xml_parts.append(f'                      </topic>')

            xml_parts.append('                    </topics>')
            xml_parts.append('                  </children>')
            xml_parts.append(f'                </topic>')

    # Add 概念 section's own questions (if any)
    if "概念" in section_data and section_data["概念"]:
        for q_text, a_text in section_data["概念"]:
            q_id = generate_id()
            xml_parts.append(f'                <topic id="{q_id}">')
            xml_parts.append(f'                  <title>{escape(q_text)}</title>')
            if a_text:
                safe_answer = escape(a_text)
                safe_answer_html = safe_answer.replace("\n", "<br/>")
                xml_parts.append('                  <notes>')
                xml_parts.append('                    <html>')
                xml_parts.append('                      <head/>')
                xml_parts.append(f'                        <body>{safe_answer_html}</body>')
                xml_parts.append('                    </html>')
                xml_parts.append('                  </notes>')
            xml_parts.append(f'                </topic>')

    xml_parts.append('              </topics>')
    xml_parts.append('            </children>')
    xml_parts.append(f'          </topic>')

    # ===== Subtopic 2: 数据结构 =====
    xml_parts.append(f'          <topic id="{ds_id}">')
    xml_parts.append('            <title>数据结构</title>')
    xml_parts.append('            <children>')
    xml_parts.append('              <topics type="attached">')

    # Add 数据类型 under 数据结构
    if "数据类型" in section_data and section_data["数据类型"]:
        ds_sub_id = generate_id()
        xml_parts.append(f'                <topic id="{ds_sub_id}">')
        xml_parts.append('                  <title>数据类型</title>')
        xml_parts.append('                  <children>')
        xml_parts.append('                    <topics type="attached">')

        for q_text, a_text in section_data["数据类型"]:
            q_id = generate_id()
            xml_parts.append(f'                      <topic id="{q_id}">')
            xml_parts.append(f'                        <title>{escape(q_text)}</title>')
            if a_text:
                safe_answer = escape(a_text)
                safe_answer_html = safe_answer.replace("\n", "<br/>")
                xml_parts.append('                        <notes>')
                xml_parts.append('                          <html>')
                xml_parts.append('                            <head/>')
                xml_parts.append(f'                              <body>{safe_answer_html}</body>')
                xml_parts.append('                          </html>')
                xml_parts.append('                        </notes>')
            xml_parts.append(f'                      </topic>')

        xml_parts.append('                    </topics>')
        xml_parts.append('                  </children>')
        xml_parts.append(f'                </topic>')

    xml_parts.append('              </topics>')
    xml_parts.append('            </children>')
    xml_parts.append(f'          </topic>')

    xml_parts.append('        </topics>')
    xml_parts.append('      </children>')
    xml_parts.append(f'    </topic>')
    xml_parts.append('  </sheet>')
    xml_parts.append('</xmap-content>')

    return "\n".join(xml_parts)


def create_xmind_file(xml_content, output_path):
    """Create XMind file (ZIP with content.xml and META-INF/manifest.xml)."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    manifest_xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">
  <file-entry full-path="content.xml" media-type="text/xml"/>
  <file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
</manifest>"""

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.xml", xml_content.encode("utf-8"))
        zf.writestr("META-INF/manifest.xml", manifest_xml.encode("utf-8"))

    print(f"XMind file created: {output_path}")


def main():
    # Parse markdown
    print("Parsing markdown...")
    section_data, standalone_questions = parse_markdown(MD_FILE)

    # Print summary
    total_questions = sum(len(qs) for qs in section_data.values()) + len(standalone_questions)
    print(f"Found sections: {list(section_data.keys())}")
    print(f"Total questions: {total_questions}")
    for section, questions in section_data.items():
        print(f"  {section}: {len(questions)} questions")
    if standalone_questions:
        print(f"  [standalone]: {len(standalone_questions)} questions")

    # Build XMind XML
    print("\nBuilding XMind XML...")
    xml_content = build_xmind_xml(section_data, standalone_questions)

    # Write XMind file
    create_xmind_file(xml_content, OUTPUT_FILE)
    print("Done!")


if __name__ == "__main__":
    main()
