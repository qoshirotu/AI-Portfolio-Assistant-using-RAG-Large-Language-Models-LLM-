import hashlib
import re
from dataclasses import asdict, dataclass
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.website_extract import clean_text


@dataclass
class PageMetadata:
    source_url: str
    source_type: str
    category: str
    page_type: str
    title: str
    slug: str
    filename: str
    path: str
    chunk_index: int = 0
    project_title: Optional[str] = None
    project_slug: Optional[str] = None
    project_canonical_id: Optional[str] = None
    description: Optional[str] = None
    published_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[str] = None
    content_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.split("/")[-1] if path else "home"


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def detect_page_type(url: str, soup: BeautifulSoup) -> str:
    slug = slug_from_url(url).lower()
    title = clean_text(soup.title.get_text(" ", strip=True) if soup.title else "").lower()
    path = urlparse(url).path.lower().strip("/")

    if slug == "home" or path == "":
        return "home"
    if slug in {"projects", "project", "works", "portfolio", "research"}:
        return "project_index"
    if path.startswith("projects/") or path.startswith("project/") or path.startswith("works/") or path.startswith("research/"):
        return "project_detail"
    if "about" in slug or "about" in title:
        return "about"
    if "contact" in slug or "contact" in title:
        return "contact"
    if "project" in title or "portfolio" in title or "research" in title:
        return "project_detail"
    if "experience" in path or "work" in path:
        return "experience_detail"
    return "generic"


def detect_category(page_type: str) -> str:
    mapping = {
        "home": "profile",
        "about": "profile",
        "contact": "contact",
        "project_index": "projects",
        "project_detail": "projects",
        "experience_detail": "experience",
        "generic": "profile",
    }
    return mapping.get(page_type, "profile")


def extract_title(soup: BeautifulSoup, slug: str) -> str:
    h1 = soup.find("h1")
    if h1:
        text = clean_text(h1.get_text(" ", strip=True))
        if text:
            return text

    if soup.title:
        text = clean_text(soup.title.get_text(" ", strip=True))
        if text:
            return text

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        return clean_text(og_title["content"])

    return slug.replace("-", " ").title()


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        return clean_text(meta_desc["content"])

    og_desc = soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.get("content"):
        return clean_text(og_desc["content"])

    first_p = soup.find("p")
    if first_p:
        text = clean_text(first_p.get_text(" ", strip=True))
        if len(text) >= 30:
            return text

    return None


def extract_date_from_meta(soup: BeautifulSoup, possible_names: list[str]) -> Optional[str]:
    for name in possible_names:
        tag = soup.find("meta", attrs={"name": name}) or soup.find("meta", attrs={"property": name})
        if tag and tag.get("content"):
            return clean_text(tag["content"])
    return None


def extract_tags(soup: BeautifulSoup) -> Optional[str]:
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    if meta_keywords and meta_keywords.get("content"):
        return clean_text(meta_keywords["content"])
    return None


def build_page_metadata(url: str, html: str, text: str, chunk_index: int = 0) -> PageMetadata:
    soup = BeautifulSoup(html, "html.parser")
    slug = slug_from_url(url)
    page_type = detect_page_type(url, soup)
    category = detect_category(page_type)
    title = extract_title(soup, slug)
    description = extract_description(soup)
    published_at = extract_date_from_meta(soup, ["article:published_time", "publish_date", "datePublished"])
    updated_at = extract_date_from_meta(soup, ["article:modified_time", "lastmod", "dateModified"])
    tags = extract_tags(soup)
    content_hash = hash_text(text)

    project_title = None
    project_slug = None
    project_canonical_id = None

    if page_type == "project_detail":
        project_title = title
        project_slug = slug
        project_canonical_id = slug

    return PageMetadata(
        source_url=url,
        source_type="website",
        category=category,
        page_type=page_type,
        title=title,
        slug=slug,
        filename=slug,
        path=url,
        chunk_index=chunk_index,
        project_title=project_title,
        project_slug=project_slug,
        project_canonical_id=project_canonical_id,
        description=description,
        published_at=published_at,
        updated_at=updated_at,
        tags=tags,
        content_hash=content_hash,
    )
