import re
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def extract_main_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    for selector in [
        "header",
        "footer",
        "nav",
        "[role='navigation']",
        "[aria-label='breadcrumb']",
        "aside",
        "form",
        "button",
    ]:
        for el in soup.select(selector):
            el.decompose()

    candidates = []
    for selector in ["main", "article", '[role="main"]']:
        for el in soup.select(selector):
            text = clean_text(el.get_text(" ", strip=True))
            if len(text) >= 200:
                candidates.append(text)

    if candidates:
        return max(candidates, key=len)

    body = soup.body or soup
    return clean_text(body.get_text(" ", strip=True))


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 120):
    text = clean_text(text)
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]

        if end < len(text):
            last_break = max(
                chunk.rfind(". "),
                chunk.rfind("! "),
                chunk.rfind("? "),
                chunk.rfind("\n"),
            )
            if last_break > int(max_chars * 0.5):
                chunk = chunk[: last_break + 1]

        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        start += max(len(chunk) - overlap, 1)

    return chunks