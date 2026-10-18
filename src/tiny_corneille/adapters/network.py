"""Download raw bytes from a URL over HTTPS only."""

import http.client
import urllib.request
from collections.abc import Callable
from typing import Any

USER_AGENT = "tiny-corneille/0.1.0 (+https://github.com/NoeFlandre/tiny-corneille)"


class DownloadError(OSError):
    """The download failed for a transport reason or was refused."""


class HttpsOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to HTTPS URLs."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,  # noqa: ANN401 - the stdlib signature is untyped
        code: int,
        msg: str,
        headers: Any,  # noqa: ANN401 - the stdlib signature is untyped
        newurl: str,
    ) -> urllib.request.Request | None:
        if not newurl.startswith("https://"):
            raise DownloadError(f"refusing redirect to non-HTTPS URL: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _default_open(request: urllib.request.Request, timeout: float) -> http.client.HTTPResponse:
    opener = urllib.request.build_opener(HttpsOnlyRedirectHandler)
    return opener.open(request, timeout=timeout)


def download(
    url: str,
    *,
    timeout: float = 30.0,
    open_url: Callable[..., Any] | None = None,
) -> bytes:
    """Return the response body of a GET request for the URL. Only HTTPS is allowed."""
    if not url.startswith("https://"):
        raise DownloadError(f"refusing non-HTTPS URL: {url}")
    # urllib capitalises header names, so the spelling of "User-Agent" is equivalent.
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})  # noqa: S310  # pragma: no mutate
    opener = _default_open if open_url is None else open_url
    try:
        with opener(request, timeout=timeout) as response:
            body: bytes = response.read()
    except (OSError, http.client.HTTPException) as error:
        raise DownloadError(str(error)) from error
    return body
