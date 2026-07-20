import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from time import perf_counter
from urllib.parse import urlparse, urlunparse

import requests
from fastembed import TextEmbedding

from app.vector_store import collection
from app.website_config import (
    SITE_URL,
    SITEMAP_URL,
    ALLOWED_PATH_KEYWORDS,
    BLOCKED_PATH_KEYWORDS,
    REQUEST_TIMEOUT,
    USER_AGENT,
    MAX_CHUNK_CHARS,
    CHUNK_OVERLAP,
    SYNC_STATE_DIR,
    SYNC_HASH_FILE,
)
from app.website_extract import extract_main_text, chunk_text
from app.website_mapping import build_page_metadata

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = TextEmbedding(model_name=MODEL_NAME, max_length=512)


def ensure_sync_dir():
    Path(SYNC_STATE_DIR).mkdir(parents=True, exist_ok=True)


def load_hash_state():
    ensure_sync_dir()
    if not os.path.exists(SYNC_HASH_FILE):
        return {}
    with open(SYNC_HASH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_hash_state(state: dict):
    ensure_sync_dir()
    with open(SYNC_HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False, sort_keys=True)


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    if not path:
        path = "/"
    return urlunparse((scheme, netloc, path, "", "", ""))


def is_allowed_url(url: str) -> bool:
    url = normalize_url(url)
    site = normalize_url(SITE_URL)

    if not url.startswith(site):
        return False

    lower = url.lower()
    if any(blocked in lower for blocked in BLOCKED_PATH_KEYWORDS):
        return False

    if lower == site.lower():
        return True

    return any(keyword in lower for keyword in ALLOWED_PATH_KEYWORDS)

def fetch_text(url: str) -> str:
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
    resp.raise_for_status()
    return resp.text


def parse_sitemap(xml_text: str):
    root = ET.fromstring(xml_text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for loc in root.findall(".//sm:loc", ns):
        if loc.text:
            urls.append(normalize_url(loc.text))
    return sorted(set(urls))


def delete_existing_url_chunks(url: str):
    try:
        existing = collection.get(where={"source_url": normalize_url(url)}, include=["metadatas"])
        ids = existing.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)
    except Exception:
        return 0


def reset_website_knowledge():
    result = collection.get(include=["metadatas"])
    ids_to_delete = []
    for _id, meta in zip(result.get("ids", []), result.get("metadatas", [])):
        if meta.get("source_type") == "website":
            ids_to_delete.append(_id)

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)

    if os.path.exists(SYNC_HASH_FILE):
        os.remove(SYNC_HASH_FILE)

    return len(ids_to_delete)


def build_chunk_records(url: str, html: str):
    url = normalize_url(url)
    text = extract_main_text(html)
    chunks = chunk_text(text, max_chars=MAX_CHUNK_CHARS, overlap=CHUNK_OVERLAP)
    base_meta = build_page_metadata(url, html, text, chunk_index=0)
    page_hash = base_meta.content_hash

    ids = []
    docs = []
    metas = []

    for idx, chunk in enumerate(chunks, start=1):
        meta = base_meta.to_dict()
        meta["chunk_index"] = idx
        meta = sanitize_metadata(meta)
        chunk_id = f"{meta['slug']}::chunk::{idx}"
        ids.append(chunk_id)
        docs.append(chunk)
        metas.append(meta)

    return ids, docs, metas, page_hash, base_meta, text

def sanitize_metadata(metadata: dict) -> dict:
    clean = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, bool):
            clean[key] = value
        elif isinstance(value, (str, int, float)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean

def sync_website():
    total_start = perf_counter()
    print("=" * 70)
    print("WEBSITE SYNC START")
    print("=" * 70)
    print("Site    :", normalize_url(SITE_URL))
    print("Sitemap :", normalize_url(SITEMAP_URL))
    print()

    state = load_hash_state()

    print("Fetching sitemap...")
    sitemap_xml = fetch_text(SITEMAP_URL)
    urls = parse_sitemap(sitemap_xml)
    urls = [u for u in urls if is_allowed_url(u)]

    print(f"Allowed URLs found: {len(urls)}")
    print()

    created = 0
    updated = 0
    skipped = 0
    failed = 0

    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{len(urls)}] {url}")
        try:
            html = fetch_text(url)
            ids, docs, metas, page_hash, base_meta, text = build_chunk_records(url, html)

            if not text or len(text.strip()) < 120:
                print("Skipped (content too short)")
                print()
                skipped += 1
                continue

            previous_hash = state.get(url)
            if previous_hash == page_hash:
                print("Skipped (no change)")
                print()
                skipped += 1
                continue

            deleted = delete_existing_url_chunks(url)
            embeddings = list(model.embed(docs))
            embeddings = [e.tolist() for e in embeddings]

            collection.add(
                ids=ids,
                documents=docs,
                embeddings=embeddings,
                metadatas=metas,
            )

            if previous_hash is None:
                created += 1
                print(
                    f"Created ({len(docs)} chunks, deleted_old={deleted}) | "
                    f"{base_meta.page_type} | {base_meta.title}"
                )
            else:
                updated += 1
                print(
                    f"Updated ({len(docs)} chunks, deleted_old={deleted}) | "
                    f"{base_meta.page_type} | {base_meta.title}"
                )

            state[url] = page_hash
            print()

        except Exception as e:
            failed += 1
            print("Failed ->", url)
            print(e)
            print()

    save_hash_state(state)

    print("=" * 70)
    print("WEBSITE SYNC FINISHED")
    print("=" * 70)
    print(f"Created : {created}")
    print(f"Updated : {updated}")
    print(f"Skipped : {skipped}")
    print(f"Failed  : {failed}")
    print(f"Total   : {len(urls)}")
    print(f"Time    : {perf_counter()-total_start:.3f}s")
    print("=" * 70)


if __name__ == "__main__":
    sync_website()