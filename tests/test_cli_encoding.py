"""回归：非 UTF-8 控制台（中文 Windows 的 GBK/cp936）下 CLI 不得因输出字符崩溃。"""

import io
import sys

from wewrite import cli


def test_force_utf8_reconfigures_gbk_stream(monkeypatch):
    raw = io.BytesIO()
    gbk_stdout = io.TextIOWrapper(raw, encoding="cp936", errors="strict")
    gbk_stderr = io.TextIOWrapper(io.BytesIO(), encoding="cp936", errors="strict")
    monkeypatch.setattr(sys, "stdout", gbk_stdout)
    monkeypatch.setattr(sys, "stderr", gbk_stderr)

    cli._force_utf8_stdio()

    # ░（U+2591）在 GBK 下无法编码，正是 diagnose 崩溃的字符
    print("░ 自检中文", file=gbk_stdout)
    gbk_stdout.flush()
    assert "░" in raw.getvalue().decode("utf-8")
    assert gbk_stderr.encoding.lower().replace("-", "") == "utf8"


def test_force_utf8_leaves_utf8_stream_untouched(monkeypatch):
    class Watchful:
        encoding = "utf-8"
        reconfigured = False

        def reconfigure(self, **_kwargs):
            self.reconfigured = True

    stdout, stderr = Watchful(), Watchful()
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(sys, "stderr", stderr)

    cli._force_utf8_stdio()

    assert stdout.reconfigured is False
    assert stderr.reconfigured is False


def test_main_works_with_gbk_stdio(monkeypatch):
    raw = io.BytesIO()
    fake_stdout = io.TextIOWrapper(raw, encoding="cp936")
    monkeypatch.setattr(sys, "argv", ["wewrite", "--version"])
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", io.TextIOWrapper(io.BytesIO(), encoding="cp936"))

    cli.main()  # 不应抛 UnicodeEncodeError

    fake_stdout.flush()
    assert cli.__version__ in raw.getvalue().decode("utf-8")


def test_force_utf8_tolerates_non_standard_stream(monkeypatch):
    """没有 reconfigure 的替身流（嵌入式宿主）应被跳过而不是报错。"""

    class FakeStream:
        encoding = "cp936"

        def reconfigure(self, **kwargs):
            raise AttributeError("no reconfigure")

    monkeypatch.setattr(sys, "stdout", FakeStream())
    monkeypatch.setattr(sys, "stderr", FakeStream())
    cli._force_utf8_stdio()  # 不抛异常即可
