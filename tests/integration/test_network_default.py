import urllib.request

import pytest

from tiny_corneille.adapters import network


class _Body:
    def __enter__(self) -> "_Body":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def read(self) -> bytes:
        return b"from the default opener"


def test_download_uses_urllib_when_no_opener_is_given(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict[str, str] = {}

    def fake_open(
        self: object, fullurl: urllib.request.Request, data: object = None, timeout: object = None
    ) -> _Body:
        seen["url"] = fullurl.full_url
        seen["timeout"] = timeout
        return _Body()

    monkeypatch.setattr(urllib.request.OpenerDirector, "open", fake_open)

    assert network.download("https://example.test/t") == b"from the default opener"
    assert seen["url"] == "https://example.test/t"
    assert seen["timeout"] == 30.0
