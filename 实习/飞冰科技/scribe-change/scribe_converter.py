from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import Request, urlopen

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


@dataclass
class Step:
    text: str
    image_name: str | None = None
    image_url: str | None = None


class ScribeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.steps: list[Step] = []
        self._capture_title = False
        self._capture_description = False
        self._step_depth = 0
        self._step_text: list[str] = []
        self._step_image: str | None = None
        self._step_image_url: str | None = None

    @staticmethod
    def _attrs(attrs):
        return dict(attrs)

    def handle_starttag(self, tag, attrs):
        attrs = self._attrs(attrs)
        testid = attrs.get("data-testid", "")
        if testid == "document-title" and not self.title:
            self._capture_title = True
        if tag == "p" and not self.description and self.title:
            self._capture_description = True
        if testid == "action-instruction":
            self._step_depth = 1
            self._step_text = []
            self._step_image = None
            self._step_image_url = None
            return
        if self._step_depth:
            if tag == "div":
                self._step_depth += 1
            if tag == "img" and (
                testid == "draggable-screenshot-image"
                or attrs.get("alt") == "Action screenshot"
            ):
                src = html.unescape(attrs.get("src", ""))
                self._step_image = Path(unquote(urlparse(src).path)).name or None
                self._step_image_url = src or None

    def handle_endtag(self, tag):
        if self._capture_title and tag == "h1":
            self._capture_title = False
        if self._capture_description and tag == "p":
            self._capture_description = False
        if self._step_depth and tag == "div":
            self._step_depth -= 1
            if self._step_depth == 0:
                text = re.sub(r"\s+", " ", " ".join(self._step_text)).strip()
                text = re.sub(r"^\d+\s+", "", text)
                if text:
                    self.steps.append(Step(text, self._step_image, self._step_image_url))

    def handle_data(self, data):
        value = data.strip()
        if not value:
            return
        if self._capture_title:
            self.title += value
        elif self._capture_description:
            self.description = (self.description + " " + value).strip()
        if self._step_depth:
            self._step_text.append(value)


def safe_extract(zip_path: Path, destination: Path) -> None:
    root = destination.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if root != target and root not in target.parents:
                raise ValueError(f"压缩包包含不安全路径：{member.filename}")
        archive.extractall(destination)


def parse_scribe(html_path: Path) -> tuple[str, str, list[Step]]:
    source = html_path.read_text(encoding="utf-8", errors="replace")
    parser = ScribeParser()
    parser.feed(source)
    unique: list[Step] = []
    seen: set[tuple[str, str | None]] = set()
    for step in parser.steps:
        key = (step.text, step.image_name)
        if key not in seen:
            seen.add(key)
            unique.append(step)
    if not unique:
        raise ValueError("没有识别到 Scribe 操作步骤，请确认网页使用“网页，全部”保存。")
    expected_match = re.search(r"\b(\d+)\s*(?:<!--.*?-->)?\s*steps?\b", source, re.I | re.S)
    if expected_match:
        expected = int(expected_match.group(1))
        if 0 < expected <= len(unique):
            unique = unique[:expected]
    return parser.title.strip() or html_path.stem, parser.description.strip(), unique


def find_image(root: Path, name: str | None) -> Path | None:
    if not name:
        return None
    exact = list(root.rglob(name))
    if exact:
        return exact[0]
    stem = Path(name).stem
    candidates = [p for p in root.rglob("*") if p.is_file() and p.stem.startswith(stem)]
    return candidates[0] if candidates else None


ALLOWED_IMAGE_HOSTS = {"colony-recorder.s3.us-west-1.amazonaws.com"}


def download_image(step: Step, destination: Path) -> Path | None:
    if not step.image_url or not step.image_name:
        return None
    parsed = urlparse(step.image_url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_IMAGE_HOSTS:
        return None
    query = parse_qs(parsed.query)
    signed_at = query.get("X-Amz-Date", [None])[0]
    expires = query.get("X-Amz-Expires", [None])[0]
    if signed_at and expires:
        try:
            deadline = dt.datetime.strptime(signed_at, "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc)
            deadline += dt.timedelta(seconds=int(expires))
            if dt.datetime.now(dt.timezone.utc) >= deadline:
                return None
        except (ValueError, TypeError):
            pass
    target = destination / step.image_name
    try:
        request = Request(step.image_url, headers={"User-Agent": "Mozilla/5.0 ScribeChange/1.1"})
        with urlopen(request, timeout=20) as response:
            content_type = response.headers.get_content_type()
            if not content_type.startswith("image/"):
                return None
            data = response.read(20 * 1024 * 1024 + 1)
        if not data or len(data) > 20 * 1024 * 1024:
            return None
        target.write_bytes(data)
        return target
    except Exception:
        return None


def set_cell_shading(cell, fill: str) -> None:
    props = cell._tc.get_or_add_tcPr()
    shade = OxmlElement("w:shd")
    shade.set(qn("w:fill"), fill)
    props.append(shade)


def set_paragraph_box(paragraph, fill: str | None = None, border: str = "D6E4F0") -> None:
    props = paragraph._p.get_or_add_pPr()
    if fill:
        shade = OxmlElement("w:shd")
        shade.set(qn("w:fill"), fill)
        props.append(shade)
    borders = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        item = OxmlElement(f"w:{edge}")
        item.set(qn("w:val"), "single")
        item.set(qn("w:sz"), "6")
        item.set(qn("w:space"), "5")
        item.set(qn("w:color"), border)
        borders.append(item)
    props.append(borders)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("第 ")
    run.font.size = Pt(9)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend((begin, instruction, separate, end))
    run = paragraph.add_run(" 页")
    run.font.size = Pt(9)


def build_docx(title: str, description: str, steps: list[Step], root: Path, output: Path, online: bool = True) -> dict:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for style_name, size, color, before, after in (
        ("Heading 1", 16, "2E74B5", 18, 10),
        ("Heading 2", 13, "2E74B5", 14, 7),
        ("Heading 3", 12, "1F4D78", 10, 5),
    ):
        style = doc.styles[style_name]
        style.font.name = "Microsoft YaHei"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)

    header = section.header.paragraphs[0]
    header.text = "SCRIBE 操作指南"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header_run = header.runs[0]
    header_run.font.name = "Microsoft YaHei"
    header_run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    header_run.font.size = Pt(8.5)
    header_run.font.color.rgb = RGBColor(107, 114, 128)
    add_page_number(section.footer.paragraphs[0])

    heading = doc.add_paragraph()
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.paragraph_format.space_after = Pt(6)
    run = heading.add_run(title)
    run.bold = True
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(24)
    run.font.color.rgb = RGBColor(31, 77, 120)
    if description:
        p = doc.add_paragraph(description)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(18)
        p.paragraph_format.line_spacing = 1.15
        for r in p.runs:
            r.font.size = Pt(10.5)
            r.font.color.rgb = RGBColor(100, 116, 139)

    divider = doc.add_paragraph()
    divider.paragraph_format.space_after = Pt(14)
    set_paragraph_box(divider, fill="EFF6FF", border="BFDBFE")
    r = divider.add_run(f"共 {len(steps)} 个步骤")
    r.bold = True
    r.font.color.rgb = RGBColor(37, 99, 235)

    image_count = 0
    missing_count = 0
    downloaded_count = 0
    download_dir = root / "_online_images"
    download_dir.mkdir(exist_ok=True)
    for index, step in enumerate(steps, 1):
        step_p = doc.add_paragraph()
        step_p.paragraph_format.space_before = Pt(10)
        step_p.paragraph_format.space_after = Pt(8)
        step_p.paragraph_format.keep_with_next = True
        step_p.paragraph_format.keep_together = True
        set_paragraph_box(step_p, fill="EFF6FF", border="93C5FD")
        r = step_p.add_run(f"  {index}  ")
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(37, 99, 235)
        text_run = step_p.add_run(f"  {step.text}")
        text_run.bold = True
        text_run.font.size = Pt(11)
        text_run.font.color.rgb = RGBColor(30, 41, 59)

        image = find_image(root, step.image_name)
        if image is None and online:
            image = download_image(step, download_dir)
            if image is not None:
                downloaded_count += 1
        if image:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(14)
            p.paragraph_format.keep_together = True
            set_paragraph_box(p, fill="FFFFFF", border="D6E4F0")
            try:
                p.add_run().add_picture(str(image), width=Inches(6.25))
                image_count += 1
            except Exception:
                p.add_run(f"[图片无法读取：{image.name}]")
                missing_count += 1
        else:
            p = doc.add_paragraph("[本地图片缺失]")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(14)
            set_paragraph_box(p, fill="F8FAFC", border="CBD5E1")
            p.runs[0].italic = True
            p.runs[0].font.color.rgb = RGBColor(156, 163, 175)
            missing_count += 1

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    with zipfile.ZipFile(output) as check:
        if "word/document.xml" not in check.namelist():
            raise ValueError("DOCX 结构校验失败")
    return {"steps": len(steps), "images": image_count, "missing": missing_count, "downloaded": downloaded_count}


def convert(input_path: str | Path, output_path: str | Path | None = None, online: bool = True) -> tuple[Path, dict]:
    source = Path(input_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(f"找不到输入文件：{source}")
    output = Path(output_path).expanduser().resolve() if output_path else source.with_suffix(".docx")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scribe-change-", dir=output.parent) as tmp:
        root = Path(tmp)
        if source.suffix.lower() == ".zip":
            safe_extract(source, root)
            html_files = sorted(root.rglob("*.html"), key=lambda p: p.stat().st_size, reverse=True)
        elif source.suffix.lower() in {".html", ".htm"}:
            root = source.parent
            html_files = [source]
        else:
            raise ValueError("仅支持 .zip、.html 或 .htm 文件")
        if not html_files:
            raise ValueError("压缩包中没有找到 HTML 文件")
        title, description, steps = parse_scribe(html_files[0])
        stats = build_docx(title, description, steps, root, output, online=online)
    return output, stats


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Scribe 文档转换器")
    root.geometry("560x230")
    root.resizable(False, False)
    path_var = tk.StringVar()
    status_var = tk.StringVar(value="请选择 Scribe ZIP 或 HTML 文件")

    frame = ttk.Frame(root, padding=24)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Scribe 转 Word", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w")
    ttk.Label(frame, text="离线转换，图片直接内嵌到 Word").pack(anchor="w", pady=(2, 18))
    row = ttk.Frame(frame)
    row.pack(fill="x")
    ttk.Entry(row, textvariable=path_var).pack(side="left", fill="x", expand=True)

    def choose():
        value = filedialog.askopenfilename(filetypes=[("Scribe 文件", "*.zip *.html *.htm")])
        if value:
            path_var.set(value)

    ttk.Button(row, text="选择文件", command=choose).pack(side="left", padx=(8, 0))

    def run():
        try:
            status_var.set("正在转换……")
            root.update_idletasks()
            out, stats = convert(path_var.get())
            status_var.set(f"完成：{stats['steps']} 步，{stats['images']} 张图片")
            messagebox.showinfo("转换完成", f"文件已生成：\n{out}\n\n在线补图：{stats['downloaded']}\n仍缺失：{stats['missing']}")
        except Exception as exc:
            status_var.set("转换失败")
            messagebox.showerror("转换失败", str(exc))

    ttk.Button(frame, text="开始转换", command=run).pack(anchor="w", pady=(16, 10))
    ttk.Label(frame, textvariable=status_var).pack(anchor="w")
    root.mainloop()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="将本地 Scribe ZIP/HTML 转换为图片内嵌的 Word")
    parser.add_argument("input", nargs="?", help="Scribe ZIP 或 HTML")
    parser.add_argument("-o", "--output", help="输出 DOCX 路径")
    parser.add_argument("--offline", action="store_true", help="只使用本地图片，不在线补图")
    parser.add_argument("--gui", action="store_true", help="启动图形界面")
    args = parser.parse_args(argv)
    if args.gui or not args.input:
        gui()
        return 0
    try:
        output, stats = convert(args.input, args.output, online=not args.offline)
        print(f"转换完成：{output}")
        print(f"步骤 {stats['steps']}，图片 {stats['images']}，在线补图 {stats['downloaded']}，缺失 {stats['missing']}")
        return 0
    except Exception as exc:
        print(f"转换失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
