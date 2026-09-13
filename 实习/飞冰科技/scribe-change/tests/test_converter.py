import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scribe_converter import Step, build_docx, download_image, parse_scribe, safe_extract


class ConverterTests(unittest.TestCase):
    def make_temp(self):
        root = Path(__file__).resolve().parents[1] / "work" / "tests"
        root.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=root)

    def test_parse_steps_and_deduplicate(self):
        with self.make_temp() as tmp:
            html = Path(tmp) / "sample.html"
            html.write_text('<h1 data-testid="document-title">标题</h1><div data-testid="action-instruction"><div>1</div><div>点击按钮</div></div><div data-testid="action-instruction"><div>1</div><div>点击按钮</div></div>', encoding="utf-8")
            title, _, steps = parse_scribe(html)
            self.assertEqual(title, "标题")
            self.assertEqual(len(steps), 1)
            self.assertEqual(steps[0].text, "点击按钮")

    def test_document_title_is_not_duplicated(self):
        with self.make_temp() as tmp:
            html = Path(tmp) / "sample.html"
            html.write_text('<h1 data-testid="document-title">标题</h1><h1 data-testid="document-title">标题</h1><div data-testid="action-instruction"><div>1</div><div>点击</div></div>', encoding="utf-8")
            title, _, _ = parse_scribe(html)
            self.assertEqual(title, "标题")

    def test_capture_remote_screenshot_url(self):
        with self.make_temp() as tmp:
            html = Path(tmp) / "sample.html"
            url = "https://colony-recorder.s3.us-west-1.amazonaws.com/files/action-a.png?token=x"
            html.write_text(f'<div data-testid="action-instruction"><div>1</div><div>点击</div><img alt="Action screenshot" src="{url}"></div>', encoding="utf-8")
            _, _, steps = parse_scribe(html)
            self.assertEqual(steps[0].image_name, "action-a.png")
            self.assertEqual(steps[0].image_url, url)

    def test_download_valid_remote_image(self):
        class Headers:
            @staticmethod
            def get_content_type():
                return "image/png"

        class Response:
            headers = Headers()
            def __enter__(self): return self
            def __exit__(self, *args): return False
            @staticmethod
            def read(_limit): return b"png-data"

        with self.make_temp() as tmp, patch("scribe_converter.urlopen", return_value=Response()):
            url = "https://colony-recorder.s3.us-west-1.amazonaws.com/files/action-a.png?X-Amz-Date=20990101T000000Z&X-Amz-Expires=900"
            result = download_image(Step("点击", "action-a.png", url), Path(tmp))
            self.assertIsNotNone(result)
            self.assertEqual(result.read_bytes(), b"png-data")

    def test_reject_zip_traversal(self):
        with self.make_temp() as tmp:
            archive = Path(tmp) / "bad.zip"
            with zipfile.ZipFile(archive, "w") as z:
                z.writestr("../bad.txt", "x")
            with self.assertRaises(ValueError):
                safe_extract(archive, Path(tmp) / "out")

    def test_respects_declared_step_count(self):
        with self.make_temp() as tmp:
            html = Path(tmp) / "sample.html"
            html.write_text('2 steps<div data-testid="action-instruction"><div>1</div><div>A</div></div><div data-testid="action-instruction"><div>2</div><div>B</div></div><div data-testid="action-instruction"><div>1</div><div>A duplicate</div></div>', encoding="utf-8")
            _, _, steps = parse_scribe(html)
            self.assertEqual([s.text for s in steps], ["A", "B"])

    def test_polished_docx_has_cards_header_and_footer(self):
        with self.make_temp() as tmp:
            out = Path(tmp) / "styled.docx"
            build_docx("标题", "简介", [Step("点击按钮")], Path(tmp), out, online=False)
            with zipfile.ZipFile(out) as z:
                document_xml = z.read("word/document.xml").decode("utf-8")
                header_xml = z.read("word/header1.xml").decode("utf-8")
                footer_xml = z.read("word/footer1.xml").decode("utf-8")
            self.assertIn('w:fill="EFF6FF"', document_xml)
            self.assertIn("w:pBdr", document_xml)
            self.assertIn("SCRIBE 操作指南", header_xml)
            self.assertIn(" PAGE ", footer_xml)


if __name__ == "__main__":
    unittest.main()
