#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate XMind files for all interview markdown files with dark theme."""

import re
import zipfile
import os
import uuid

MD_DIR = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\md_output"
OUTPUT_DIR = r"D:\Code\JavaProjects\Obsidian-vault\八股\小林coding\小林coding\mindmap"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Manual curated module definitions for each file
# Format: "filename.md" -> (center_topic_title, [module_names])
FILES_CONFIG = {
    # 2.Java基础面试篇
    "2.Java基础面试篇.md": ("Java基础", [
        "概念", "数据类型", "面向对象", "关键字",
        "深拷贝和浅拷贝", "泛型", "对象", "反射", "注解",
        "异常", "object", "Java 新特性", "序列化",
        "设计模式", "I/O", "其他"
    ]),
    # 3.Java集合面试篇
    "3.Java集合面试篇.md": ("Java集合", [
        "概念", "List", "Map", "Set"
    ]),
    # 4.Java并发面试篇
    "4.Java并发面试篇.md": ("Java并发", [
        "多线程", "并发安全", "线程池", "场景"
    ]),
    # 5.Java虚拟机面试篇
    "5.Java虚拟机面试篇.md": ("Java虚拟机", [
        "内存模型", "类初始化和类加载", "对象的生命周期", "垃圾回收"
    ]),
    # 6.Spring面试篇
    "6.Spring面试篇.md": ("Spring", [
        "Spring", "SpringMVC", "SpringBoot", "Mybatis", "SpringCloud"
    ]),
    # 7.MySQL面试篇
    "7.MySQL面试篇.md": ("MySQL", [
        "SQL基础", "存储引擎", "索引", "事务", "锁", "日志", "性能调优", "架构"
    ]),
    # 8.Redis面试篇
    "8.Redis面试篇.md": ("Redis", [
        "数据结构", "线程模型", "事务", "持久化", "集群", "场景"
    ]),
    # 9.计算机网络面试篇
    "9.计算机网络面试篇.md": ("计算机网络", [
        "网络模型", "应用层", "传输层", "网络场景", "网络攻击"
    ]),
    # 10.操作系统面试篇
    "10.操作系统面试篇.md": ("操作系统", [
        "用户态和内核态", "进程管理", "锁", "内存管理", "中断", "网络 i/o"
    ]),
    # 11.数据结构与算法面试篇 - no content, skip
    # 12.消息队列面试篇
    "12.消息队列面试篇.md": ("消息队列", [
        "消息队列场景", "RocketMQ", "kafka", "RabbitMQ"
    ]),
}

# Skip files with no content or intro-only
SKIP_FILES = [
    "1.Java面试题介绍.md",
    "11.数据结构与算法面试篇.md",
]


def gen_id():
    return uuid.uuid4().hex[:24]


def escape_xml(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace('"', "&quot;")
    s = s.replace("'", "&apos;")
    return s


def text_to_html_body(text):
    safe = escape_xml(text)
    safe = safe.replace("\n", "<br/>")
    return safe


def parse_questions(md_path, modules):
    """Parse markdown and return {module_name: [(question, answer)]}."""
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Remove front matter
    text = re.sub(r'^---.*?---\s*', "", text, flags=re.DOTALL).strip()

    # Remove main title heading (the one that matches center topic)
    first_hash = text.find("# ")
    if first_hash >= 0:
        end_of_title = text.find("\n", first_hash)
        if end_of_title > first_hash:
            text = text[end_of_title:].strip()

    # Split into modules
    module_content = {}
    current_module = None
    current_lines = []

    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and stripped[2:] in modules:
            if current_module:
                module_content[current_module] = "\n".join(current_lines)
            current_module = stripped[2:]
            current_lines = []
        elif current_module:
            current_lines.append(line)

    if current_module:
        module_content[current_module] = "\n".join(current_lines)

    # Parse questions from each module
    module_questions = {}
    for mod_name, content in module_content.items():
        parts = re.split(r'^# (.+)$', content, flags=re.MULTILINE)
        questions = []
        i = 1
        while i < len(parts):
            question = parts[i].strip()
            answer = parts[i + 1].strip() if i + 1 < len(parts) else ""
            if question:
                questions.append((question, answer))
            i += 2
        module_questions[mod_name] = questions

    return module_questions


def build_content_xml(center_title, module_questions, modules_order):
    """Build content.xml with structure and dark theme reference."""
    root_id = gen_id()
    sheet_id = "sheet-" + gen_id()
    theme_id = "dark-theme"

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0"')
    lines.append('  xmlns:fo="http://www.w3.org/1999/XSL/Format"')
    lines.append('  xmlns:svg="http://www.w3.org/2000/svg"')
    lines.append('  xmlns:xhtml="http://www.w3.org/1999/xhtml"')
    lines.append('  xmlns:xlink="http://www.w3.org/1999/xlink"')
    lines.append('  version="2.0">')
    lines.append(f'  <sheet id="{sheet_id}" theme="{theme_id}">')
    lines.append(f'    <topic id="{root_id}">')
    lines.append(f'      <title>{escape_xml(center_title)}</title>')
    lines.append('      <children>')
    lines.append('        <topics type="attached">')

    for mod_name in modules_order:
        if mod_name not in module_questions:
            continue
        questions = module_questions[mod_name]
        if not questions:
            continue

        mod_id = gen_id()
        lines.append(f'          <topic id="{mod_id}">')
        lines.append(f'            <title>{escape_xml(mod_name)}</title>')
        lines.append('            <children>')
        lines.append('              <topics type="attached">')

        for q_text, a_text in questions:
            q_id = gen_id()
            lines.append(f'                <topic id="{q_id}">')
            lines.append(f'                  <title>{escape_xml(q_text)}</title>')
            if a_text:
                html_body = text_to_html_body(a_text)
                lines.append('                  <notes>')
                lines.append('                    <html>')
                lines.append('                      <head/>')
                lines.append(f'                        <body><p>{html_body}</p></body>')
                lines.append('                    </html>')
                lines.append('                  </notes>')
            lines.append(f'                </topic>')

        lines.append('              </topics>')
        lines.append('            </children>')
        lines.append(f'          </topic>')

    lines.append('        </topics>')
    lines.append('      </children>')
    lines.append(f'    </topic>')
    lines.append('  </sheet>')
    lines.append('</xmap-content>')
    return "\n".join(lines)


def build_styles_xml():
    """Build styles.xml with dark theme."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<style xmlns="urn:xmind:xmap:xmlns:style:2.0"')
    lines.append('  xmlns:fo="http://www.w3.org/1999/XSL/Format"')
    lines.append('  xmlns:svg="http://www.w3.org/2000/svg"')
    lines.append('  xmlns:xhtml="http://www.w3.org/1999/xhtml"')
    lines.append('  xmlns:xlink="http://www.w3.org/1999/xlink">')
    lines.append('  <theme id="dark-theme">')
    # Central topic
    lines.append('    <topic central="true">')
    lines.append('      <topic-properties')
    lines.append('        shape-class="org.xmind.topicShape.roundedRect"')
    lines.append('        line-color="#4FC3F7"')
    lines.append('        fill-color="#1565C0"')
    lines.append('        text-color="#FFFFFF"')
    lines.append('        line-width="2pt"')
    lines.append('        font-size="20"')
    lines.append('        font-weight="bold"/>')
    lines.append('    </topic>')
    # Main topic (module level)
    lines.append('    <topic main="true">')
    lines.append('      <topic-properties')
    lines.append('        shape-class="org.xmind.topicShape.roundedRect"')
    lines.append('        line-color="#4FC3F7"')
    lines.append('        fill-color="#1E3A5F"')
    lines.append('        text-color="#E0E0E0"')
    lines.append('        line-width="1.5pt"')
    lines.append('        font-size="16"')
    lines.append('        font-weight="bold"/>')
    lines.append('    </topic>')
    # Subtopic (question level)
    lines.append('    <topic subtopic="true">')
    lines.append('      <topic-properties')
    lines.append('        shape-class="org.xmind.topicShape.roundedRect"')
    lines.append('        fill-color="#2D2D2D"')
    lines.append('        text-color="#E0E0E0"')
    lines.append('        line-color="#555555"')
    lines.append('        line-width="1pt"')
    lines.append('        font-size="12"/>')
    lines.append('    </topic>')
    # Fallback
    lines.append('    <topic>')
    lines.append('      <topic-properties')
    lines.append('        shape-class="org.xmind.topicShape.roundedRect"')
    lines.append('        fill-color="#333333"')
    lines.append('        text-color="#CCCCCC"')
    lines.append('        line-color="#666666"')
    lines.append('        line-width="1pt"/>')
    lines.append('    </topic>')
    # Relationship
    lines.append('    <relationship>')
    lines.append('      <relationship-properties')
    lines.append('        line-color="#4FC3F7"')
    lines.append('        line-width="1pt"/>')
    lines.append('    </relationship>')
    # Sheet background
    lines.append('    <sheet>')
    lines.append('      <sheet-properties')
    lines.append('        background-color="#1A1A2E"/>')
    lines.append('    </sheet>')
    lines.append('  </theme>')
    lines.append('</style>')
    return "\n".join(lines)


def build_manifest_xml(files):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0">')
    for f in files:
        lines.append(f'  <file-entry full-path="{f}" media-type="text/xml"/>')
    lines.append('</manifest>')
    return "\n".join(lines)


def build_metadata_xml(filename):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
    lines.append('<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">')
    lines.append('  <author>')
    lines.append('    <name>Sisyphus</name>')
    lines.append('  </author>')
    lines.append(f'  <created>2026-07-09 21:00:00</created>')
    lines.append(f'  <source>{escape_xml(filename)}</source>')
    lines.append('</meta>')
    return "\n".join(lines)


def create_xmind(output_path, content_xml, styles_xml, manifest_xml, metadata_xml):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.xml", content_xml.encode("utf-8"))
        zf.writestr("styles.xml", styles_xml.encode("utf-8"))
        zf.writestr("META-INF/manifest.xml", manifest_xml.encode("utf-8"))
        zf.writestr("metadata.xml", metadata_xml.encode("utf-8"))


def process_file(md_filename, center_title, modules_order):
    md_path = os.path.join(MD_DIR, md_filename)
    if not os.path.exists(md_path):
        print(f"  SKIP: {md_path} not found")
        return False

    # Output name: keep the numeric prefix, change extension
    base = os.path.splitext(md_filename)[0]
    xmind_filename = base + ".xmind"
    output_path = os.path.join(OUTPUT_DIR, xmind_filename)

    print(f"\n{'='*60}")
    print(f"Processing: {md_filename}")
    print(f"Output: {xmind_filename}")
    print(f"{'='*60}")

    module_questions = parse_questions(md_path, modules_order)

    total_q = sum(len(qs) for qs in module_questions.values())
    if total_q == 0:
        print(f"  WARNING: No questions found!")
        return False

    print(f"  Modules: {len(module_questions)}")
    for m in modules_order:
        qs = module_questions.get(m, [])
        if qs:
            print(f"    [{m}]: {len(qs)} questions")

    content_xml = build_content_xml(center_title, module_questions, modules_order)
    styles_xml = build_styles_xml()
    manifest_xml = build_manifest_xml([
        "content.xml", "styles.xml",
        "META-INF/manifest.xml", "metadata.xml"
    ])
    metadata_xml = build_metadata_xml(md_filename)

    create_xmind(output_path, content_xml, styles_xml, manifest_xml, metadata_xml)

    file_size = os.path.getsize(output_path)
    with zipfile.ZipFile(output_path, "r") as zf:
        title_count = zf.read("content.xml").count(b"<title>")

    print(f"  Total nodes: {title_count}")
    print(f"  File size: {file_size} bytes")
    print(f"  Created: {xmind_filename}")
    return True


def main():
    print("XMind Mind Map Generator - 小林coding面试题")
    print("=" * 60)

    success_count = 0
    skip_count = 0

    # Process all files in sorted order
    for md_filename in sorted(os.listdir(MD_DIR)):
        if not md_filename.endswith(".md"):
            continue
        if md_filename in SKIP_FILES:
            print(f"\nSKIP: {md_filename} (no content / intro only)")
            skip_count += 1
            continue
        if md_filename not in FILES_CONFIG:
            print(f"\nSKIP: {md_filename} (no config defined)")
            skip_count += 1
            continue

        center_title, modules_order = FILES_CONFIG[md_filename]
        if process_file(md_filename, center_title, modules_order):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Summary: {success_count} files generated, {skip_count} files skipped")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
