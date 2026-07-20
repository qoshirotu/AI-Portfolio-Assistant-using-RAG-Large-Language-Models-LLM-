import json
import os
from hashlib import sha256
from pathlib import Path
from time import perf_counter

from fastembed import TextEmbedding

from app.vector_store import collection
from app.website_extract import chunk_text

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = TextEmbedding(model_name=MODEL_NAME, max_length=512)

BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_PATH = BASE_DIR / "knowledge"
SYNC_STATE_DIR = BASE_DIR / ".sync_state"
MANUAL_HASH_FILE = SYNC_STATE_DIR / "manual_hashes.json"
MAX_CHUNK_CHARS = 700
CHUNK_OVERLAP = 120
MIN_TEXT_LENGTH = 20


def ensure_sync_dir():
    SYNC_STATE_DIR.mkdir(parents=True, exist_ok=True)



def load_hash_state() -> dict:
    ensure_sync_dir()
    if not MANUAL_HASH_FILE.exists():
        return {}
    with open(MANUAL_HASH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)



def save_hash_state(state: dict):
    ensure_sync_dir()
    with open(MANUAL_HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False, sort_keys=True)



def normalize_text(text: str) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").split("\n")]
    cleaned = []
    previous_blank = False
    for line in lines:
        if not line:
            if not previous_blank:
                cleaned.append("")
            previous_blank = True
            continue
        cleaned.append(line)
        previous_blank = False
    return "\n".join(cleaned).strip()



def compute_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()



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



def delete_manual_knowledge():
    result = collection.get(include=["metadatas"])
    ids_to_delete = []

    for _id, meta in zip(result.get("ids", []), result.get("metadatas", [])):
        if meta.get("source_type", "manual") == "manual":
            ids_to_delete.append(_id)

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)

    return len(ids_to_delete)



def delete_existing_file_chunks(relative_path: str) -> int:
    try:
        existing = collection.get(where={"path": relative_path, "source_type": "manual"}, include=["metadatas"])
        ids = existing.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)
    except Exception:
        return 0



def build_chunk_records(file: Path, knowledge_root: Path):
    relative_path = file.relative_to(knowledge_root).as_posix()
    raw_text = file.read_text(encoding="utf-8")
    text = normalize_text(raw_text)

    if not text or len(text.strip()) < MIN_TEXT_LENGTH:
        return None

    file_hash = compute_hash(text)
    chunks = chunk_text(text, max_chars=MAX_CHUNK_CHARS, overlap=CHUNK_OVERLAP)
    if not chunks:
        return None

    category = file.parent.name
    if file.name.lower() == "personal_information.txt":
        category = "personal"
    elif file.name.lower() == "about.txt":
        category = "about"
    elif file.name.lower() == "education.txt":
        category = "education"
    elif file.name.lower() == "skills.txt":
        category = "skills"
    stem = file.stem.replace("_", " ").replace("-", " ").strip()
    title = " ".join(word.capitalize() for word in stem.split())

    ids = []
    docs = []
    metas = []

    total_chunks = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        chunk_id = f"manual::{relative_path}::chunk::{idx}"
        metadata = {
            "category": category,
            "filename": file.name,
            "path": relative_path,
            "source_type": "manual",
            "title": title,
            "slug": file.stem,
            "chunk_index": idx,
            "chunk_count": total_chunks,
            "content_hash": file_hash,
        }
        ids.append(chunk_id)
        docs.append(chunk)
        metas.append(sanitize_metadata(metadata))

    return ids, docs, metas, file_hash, title, len(text), total_chunks



def delete_stale_manual_docs(current_paths: set, state: dict) -> int:
    stale_paths = sorted(set(state.keys()) - current_paths)
    deleted_count = 0

    for relative_path in stale_paths:
        deleted_count += delete_existing_file_chunks(relative_path)
        state.pop(relative_path, None)

    return deleted_count



def ingest(force_full: bool = False):
    total_start = perf_counter()

    print("=" * 60)
    print("KNOWLEDGE INGEST")
    print("=" * 60)
    print("Knowledge Path :", KNOWLEDGE_PATH)
    print()

    if not KNOWLEDGE_PATH.exists():
        raise FileNotFoundError("Folder knowledge tidak ditemukan.")

    ensure_sync_dir()
    state = {} if force_full else load_hash_state()

    if force_full:
        print("Force full ingest mode...")
        deleted = delete_manual_knowledge()
        print(f"Deleted manual records: {deleted}")
        print("Done.\n")

    files = sorted(KNOWLEDGE_PATH.rglob("*.txt"))
    print(f"Found {len(files)} knowledge files.\n")

    created = 0
    updated = 0
    skipped = 0
    failed = 0
    deleted_stale = 0

    current_paths = {file.relative_to(KNOWLEDGE_PATH).as_posix() for file in files}
    if not force_full:
        deleted_stale = delete_stale_manual_docs(current_paths, state)

    for index, file in enumerate(files, start=1):
        print(f"[{index}/{len(files)}] {file.name}")
        try:
            built = build_chunk_records(file, KNOWLEDGE_PATH)
            if built is None:
                print("Skipped (empty/too short)\n")
                skipped += 1
                continue

            ids, docs, metas, file_hash, title, text_length, chunk_count = built
            relative_path = file.relative_to(KNOWLEDGE_PATH).as_posix()
            previous_hash = state.get(relative_path)

            if not force_full and previous_hash == file_hash:
                print(f"Skipped (no change) | chunks={chunk_count} | chars={text_length}\n")
                skipped += 1
                continue

            deleted_old = delete_existing_file_chunks(relative_path)
            embeddings = list(model.embed(docs))
            embeddings = [e.tolist() for e in embeddings]

            collection.add(
                ids=ids,
                documents=docs,
                embeddings=embeddings,
                metadatas=metas,
            )

            state[relative_path] = file_hash

            if previous_hash is None or force_full:
                created += 1
                print(
                    f"Created ({chunk_count} chunks, deleted_old={deleted_old}) | "
                    f"{metas[0]['category']} | {title}"
                )
            else:
                updated += 1
                print(
                    f"Updated ({chunk_count} chunks, deleted_old={deleted_old}) | "
                    f"{metas[0]['category']} | {title}"
                )
            print()

        except Exception as e:
            failed += 1
            print("Failed")
            print(e)
            print()

    save_hash_state(state)

    print("=" * 60)
    print("INGEST FINISHED")
    print("=" * 60)
    print(f"Created      : {created}")
    print(f"Updated      : {updated}")
    print(f"Skipped      : {skipped}")
    print(f"DeletedStale : {deleted_stale}")
    print(f"Failed       : {failed}")
    print(f"Total Files  : {len(files)}")
    print(f"Time         : {perf_counter() - total_start:.3f}s")
    print("=" * 60)


if __name__ == "__main__":
    ingest()