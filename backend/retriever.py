import re
from collections import defaultdict
from time import perf_counter

from fastembed import TextEmbedding

from app.vector_store import collection

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model = None

CATEGORY_KEYWORDS = {
    "projects": ["project", "projects", "projek", "proyek", "portfolio", "penelitian", "research", "karya", "design", "brand", "guidelines"],
    "experience": ["experience", "pengalaman", "intern", "internship", "kerja", "pekerjaan", "organisasi", "leadership"],
    "education": ["education", "pendidikan", "kuliah", "kampus", "universitas", "gpa", "tesis", "thesis"],
    "skills": ["skill", "skills", "keahlian", "kemampuan", "tools", "programming", "python", "sql"],
    "contact": ["contact", "kontak", "email", "linkedin", "github", "phone", "nomor", "hubungi", "menghubungi"],
    "profile": ["about", "profil", "profile", "siapa", "tentang", "introduce", "background", "career"],
    "personal": ["cat", "pet", "girlfriend", "boyfriend", "relationship", "dating", "hobi", "hobby", "favorite", "kucing", "pacar", "hubungan"],
}

STOPWORDS = {
    "apakah", "pernah", "yang", "dan", "atau", "di", "ke", "dari", "untuk", "dengan", "itu", "ini", "ada",
    "the", "is", "are", "of", "to", "for", "and", "in", "on", "a", "an", "did", "does", "do",
    "qoshi", "what", "who", "how", "when", "where", "sebutkan", "tolong", "all", "please",
}

MANUAL_PRIORITY_CATEGORIES = {"profile", "contact", "education", "skills", "personal", "about"}
SEMANTIC_PRIORITY_CATEGORIES = {"projects", "experience"}
LIST_PATTERNS = [
    "semua project", "semua projek", "semua proyek",
    "apa saja project", "apa saja projek", "apa saja proyek",
    "daftar project", "daftar projek", "daftar proyek",
    "list project", "list projek", "list proyek",
    "all projects", "qoshi's all projects", "list all projects",
]

PROFILE_SUMMARY_PATTERNS = [
    "who is qoshi",
    "tell me about qoshi",
    "introduce qoshi",
    "about qoshi",
    "qoshi background",
    "qoshi profile",
    "professional summary",
    "siapa qoshi",
    "ceritakan tentang qoshi",
    "jelaskan qoshi",
    "tentang qoshi",
    "profil qoshi",
    "latar belakang qoshi",
    "perkenalkan qoshi",
]

PERSONAL_FACT_PATTERNS = [
    "cat name", "pet name", "girlfriend", "boyfriend", "relationship", "dating", "favorite", "hobby", "hobbies",
    "nama kucing", "kucing", "pacar", "hubungan", "hobi", "favorit", "hewan peliharaan",
]

_doc_cache = {"ids": [], "documents": [], "metadatas": [], "loaded": False}
_lower_cache = {"texts": [], "built_for": None}


def get_model():
    global _model
    if _model is None:
        start = perf_counter()
        print("Loading Embedding Model (fastembed/ONNX)...")
        _model = TextEmbedding(model_name=MODEL_NAME, max_length=512)
        print(f"Model Load Time : {perf_counter()-start:.3f}s")
    return _model



def tokenize(text: str):
    return re.findall(r"\w+", text.lower())



def meaningful_tokens(text: str):
    return [t for t in tokenize(text) if len(t) >= 2 and t not in STOPWORDS]



def is_list_query(question: str):
    q = question.lower()
    if any(pattern in q for pattern in LIST_PATTERNS):
        return True
    project_terms = any(t in q for t in ["project", "projects", "projek", "proyek"])
    listing_terms = any(t in q for t in ["semua", "apa saja", "daftar", "list", "all"])
    return project_terms and listing_terms



def is_profile_summary_query(question: str) -> bool:
    q = (question or "").strip().lower()
    return any(pattern in q for pattern in PROFILE_SUMMARY_PATTERNS)



def is_personal_fact_query(question: str) -> bool:
    q = (question or "").strip().lower()
    return any(pattern in q for pattern in PERSONAL_FACT_PATTERNS)



def detect_category(question: str):
    q = question.lower()
    if is_list_query(question):
        return "projects"
    if is_personal_fact_query(question):
        return "personal"
    if is_profile_summary_query(question):
        return "profile"

    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in q:
                score += 1
        if score > 0:
            scores[category] = score

    if any(t in q for t in ["project", "projects", "projek", "proyek", "portfolio", "research", "karya"]):
        scores["projects"] = scores.get("projects", 0) + 3

    if not scores:
        return None
    return max(scores, key=scores.get)



def build_cache(force: bool = False):
    if _doc_cache["loaded"] and not force:
        return
    start = perf_counter()
    result = collection.get(include=["documents", "metadatas"])
    _doc_cache["ids"] = result["ids"]
    _doc_cache["documents"] = result["documents"]
    _doc_cache["metadatas"] = result["metadatas"]
    _doc_cache["loaded"] = True
    _lower_cache["texts"] = []
    _lower_cache["built_for"] = None
    print(f"Doc Cache Built ({len(result['documents'])} docs) : {perf_counter()-start:.3f}s")



def invalidate_cache():
    _doc_cache["loaded"] = False
    _lower_cache["texts"] = []
    _lower_cache["built_for"] = None



def _get_lower_texts():
    build_cache()
    if _lower_cache["built_for"] is not id(_doc_cache["documents"]):
        _lower_cache["texts"] = [d.lower() for d in _doc_cache["documents"]]
        _lower_cache["built_for"] = id(_doc_cache["documents"])
    return _lower_cache["texts"]



def safe_meta(meta):
    return meta or {}



def get_doc_key(meta, doc=None):
    meta = safe_meta(meta)
    return (
        meta.get("source_url")
        or meta.get("path")
        or meta.get("project_canonical_id")
        or meta.get("filename")
        or (doc[:120] if doc else None)
    )



def is_home_meta(meta):
    meta = safe_meta(meta)
    filename = (meta.get("filename") or "").lower()
    source_url = (meta.get("source_url") or "").rstrip("/").lower()
    return filename == "home" or source_url.endswith("framer.website")



def is_website_project_detail(meta):
    meta = safe_meta(meta)
    return (
        meta.get("source_type") == "website"
        and meta.get("category") == "projects"
        and meta.get("page_type") == "project_detail"
        and not is_home_meta(meta)
    )



def is_website_project_index(meta):
    meta = safe_meta(meta)
    return (
        meta.get("source_type") == "website"
        and meta.get("category") == "projects"
        and meta.get("page_type") == "project_index"
    )



def is_manual_project(meta):
    meta = safe_meta(meta)
    return meta.get("source_type") == "manual" and meta.get("category") == "projects"



def get_project_group_key(meta, doc=None):
    meta = safe_meta(meta)
    return (
        meta.get("project_canonical_id")
        or meta.get("project_slug")
        or meta.get("source_url")
        or meta.get("filename")
        or get_doc_key(meta, doc)
    )



def rank_manual_boost(meta, detected_category):
    meta = safe_meta(meta)
    boost = 0.0
    if meta.get("source_type") == "manual":
        boost += 1.5
        if detected_category in MANUAL_PRIORITY_CATEGORIES:
            boost += 4.0
        if detected_category == "projects":
            boost -= 1.0
    return boost



def rank_website_project_boost(meta, detected_category, list_query=False):
    meta = safe_meta(meta)
    boost = 0.0
    if detected_category == "projects":
        if is_website_project_detail(meta):
            boost += 7.5 if list_query else 5.0
        elif is_website_project_index(meta):
            boost += 5.5 if list_query else 3.5
        elif meta.get("source_type") == "website" and meta.get("category") == "projects":
            boost += 2.0
    elif detected_category == "experience" and meta.get("source_type") == "website" and meta.get("category") == "experience":
        boost += 2.5
    return boost



def rank_profile_summary_boost(meta):
    meta = safe_meta(meta)
    category = (meta.get("category") or "").lower()
    source_type = meta.get("source_type")
    filename = (meta.get("filename") or "").lower()

    boost = 0.0
    if category == "about":
        boost += 8.0
    elif category == "profile":
        boost += 6.0
    elif category == "education":
        boost += 5.0
    elif category == "skills":
        boost += 5.0
    elif category == "experience":
        boost += 4.5
    elif category == "projects":
        boost += 2.5
    elif category == "personal":
        boost -= 8.0

    if source_type == "manual":
        boost += 1.5
    if filename == "personal_information.txt":
        boost -= 10.0
    return boost



def rank_personal_fact_boost(meta):
    meta = safe_meta(meta)
    category = (meta.get("category") or "").lower()
    filename = (meta.get("filename") or "").lower()
    boost = 0.0
    if category == "personal":
        boost += 10.0
    elif category == "profile":
        boost += 1.0
    else:
        boost -= 2.0
    if filename == "personal_information.txt":
        boost += 4.0
    return boost



def score_category_candidate(doc, meta, q_tokens, detected_category, list_query=False):
    meta = safe_meta(meta)
    text = (doc or "").lower()
    filename = (meta.get("filename") or "").lower()
    source_url = (meta.get("source_url") or "").lower()

    score = 0.0
    for token in q_tokens:
        if token in text:
            score += 3.0
        if token in filename:
            score += 2.5
        if token in source_url:
            score += 1.5

    score += rank_manual_boost(meta, detected_category)
    score += rank_website_project_boost(meta, detected_category, list_query=list_query)

    if detected_category == "projects" and is_home_meta(meta):
        score -= 4.0
    if detected_category == "projects" and meta.get("category") != "projects":
        score -= 3.0
    return score



def category_search(category: str, question: str, top_k: int = 12):
    build_cache()
    q_tokens = meaningful_tokens(question)
    list_query = is_list_query(question)
    candidates = []

    for doc, meta in zip(_doc_cache["documents"], _doc_cache["metadatas"]):
        meta = safe_meta(meta)
        if meta.get("category") != category:
            continue
        score = score_category_candidate(doc, meta, q_tokens, category, list_query=list_query)
        candidates.append((score, doc, meta))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    top = candidates[:top_k]
    return {"documents": [t[1] for t in top], "metadatas": [t[2] for t in top]}



def keyword_search(question: str, top_k: int = 12):
    start = perf_counter()
    query_tokens = meaningful_tokens(question)
    if not query_tokens:
        return None

    detected_category = detect_category(question)
    list_query = is_list_query(question)
    profile_summary_query = is_profile_summary_query(question)
    personal_fact_query = is_personal_fact_query(question)

    lower_texts = _get_lower_texts()
    metas = _doc_cache["metadatas"]
    docs = _doc_cache["documents"]

    scored = []
    for i, text in enumerate(lower_texts):
        token_hits = 0
        exact_phrase_bonus = 0.0

        for token in query_tokens:
            if token in text:
                token_hits += 1

        phrases = [" ".join(query_tokens[j:j+2]) for j in range(len(query_tokens) - 1)]
        for phrase in phrases:
            if phrase and phrase in text:
                exact_phrase_bonus += 3.0

        if token_hits == 0 and not profile_summary_query:
            continue

        meta = safe_meta(metas[i])
        score = token_hits * 2.5 + exact_phrase_bonus
        filename = (meta.get("filename") or "").lower()
        source_url = (meta.get("source_url") or "").lower()
        category = (meta.get("category") or "").lower()

        score += rank_manual_boost(meta, detected_category)
        score += rank_website_project_boost(meta, detected_category, list_query=list_query)

        if detected_category and category == detected_category:
            score += 2.0

        if profile_summary_query:
            score += rank_profile_summary_boost(meta)
        if personal_fact_query:
            score += rank_personal_fact_boost(meta)

        for token in query_tokens:
            if token in filename:
                score += 3.0
            if token in source_url:
                score += 2.0

        if detected_category == "projects" and is_home_meta(meta):
            score -= 4.0
        if detected_category == "projects" and category != "projects":
            score -= 3.0

        scored.append((score, docs[i], meta))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    print(f"Keyword Search : {perf_counter()-start:.3f}s ({len(scored)} matched)")
    if not top:
        return None

    for score, _, meta in top[:8]:
        print(f"KW -> {meta.get('filename', '?')} | score={score:.2f}")

    return {"documents": [t[1] for t in top], "metadatas": [t[2] for t in top]}



def semantic_search(question: str, top_k: int = 12, where: dict | None = None):
    model = get_model()

    embed_start = perf_counter()
    question_embedding = list(model.embed([question]))[0].tolist()
    print(f"Embedding    : {perf_counter()-embed_start:.3f}s")

    chroma_start = perf_counter()
    query_kwargs = {
        "query_embeddings": [question_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        query_kwargs["where"] = where

    result = collection.query(**query_kwargs)
    print(f"Chroma Query : {perf_counter()-chroma_start:.3f}s")

    docs = []
    metas = []
    distances = result.get("distances", [[]])[0]

    for doc, meta, distance in zip(result["documents"][0], result["metadatas"][0], distances):
        meta = safe_meta(meta)
        print(f"SEM -> {meta.get('filename', '?')} | distance={distance:.3f}")
        docs.append(doc)
        metas.append(meta)

    if not docs:
        return None

    return {"documents": docs, "metadatas": metas}



def reciprocal_rank_fusion(named_results, k: int = 60):
    scores = defaultdict(float)
    doc_payload = {}

    for source_name, result in named_results:
        if not result:
            continue
        for rank, (doc, meta) in enumerate(zip(result["documents"], result["metadatas"]), start=1):
            key = get_doc_key(meta, doc)
            scores[key] += 1.0 / (k + rank)
            if key not in doc_payload:
                doc_payload[key] = {"document": doc, "metadata": meta, "sources": [source_name]}
            else:
                doc_payload[key]["sources"].append(source_name)
                if is_website_project_detail(meta):
                    doc_payload[key]["document"] = doc
                    doc_payload[key]["metadata"] = meta

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    fused_docs = []
    fused_metas = []

    for key, score in ranked:
        payload = doc_payload[key]
        meta = dict(payload["metadata"])
        meta["fusion_score"] = round(score, 6)
        meta["fusion_sources"] = ",".join(sorted(set(payload["sources"])))
        fused_docs.append(payload["document"])
        fused_metas.append(meta)

    if not fused_docs:
        return None
    return {"documents": fused_docs, "metadatas": fused_metas}



def dedup_grouped_results(result, top_k: int = 8, by_project: bool = False):
    if not result:
        return None

    docs = []
    metas = []
    seen = set()

    for doc, meta in zip(result["documents"], result["metadatas"]):
        if by_project:
            key = get_project_group_key(meta, doc)
        else:
            key = (get_doc_key(meta, doc), meta.get("chunk_index", 0))

        if key in seen:
            continue
        seen.add(key)
        docs.append(doc)
        metas.append(meta)
        if len(docs) >= top_k:
            break

    if not docs:
        return None
    return {"documents": docs, "metadatas": metas}



def prioritize_project_results(result, top_k: int = 12):
    if not result:
        return None

    grouped = {}
    for doc, meta in zip(result["documents"], result["metadatas"]):
        key = get_project_group_key(meta, doc)
        current = grouped.get(key)
        current_score = meta.get("fusion_score", 0)
        current_is_detail = is_website_project_detail(meta)

        if current is None:
            grouped[key] = (doc, meta)
            continue

        _, existing_meta = current
        existing_score = existing_meta.get("fusion_score", 0)
        existing_is_detail = is_website_project_detail(existing_meta)

        if current_is_detail and not existing_is_detail:
            grouped[key] = (doc, meta)
        elif current_is_detail == existing_is_detail and current_score > existing_score:
            grouped[key] = (doc, meta)

    ranked = sorted(
        grouped.values(),
        key=lambda item: (
            1 if is_website_project_detail(item[1]) else 0,
            1 if is_website_project_index(item[1]) else 0,
            item[1].get("fusion_score", 0),
        ),
        reverse=True,
    )

    docs = [doc for doc, _ in ranked[:top_k]]
    metas = [meta for _, meta in ranked[:top_k]]
    return {"documents": docs, "metadatas": metas} if docs else None



def prioritize_profile_summary_results(result, top_k: int = 8):
    if not result:
        return None

    scored = []
    for doc, meta in zip(result["documents"], result["metadatas"]):
        meta = safe_meta(meta)
        score = meta.get("fusion_score", 0) + rank_profile_summary_boost(meta)
        scored.append((score, doc, meta))

    scored.sort(key=lambda x: x[0], reverse=True)

    docs = [doc for _, doc, _ in scored[:top_k]]
    metas = [meta for _, _, meta in scored[:top_k]]
    return {"documents": docs, "metadatas": metas} if docs else None



def prioritize_personal_fact_results(result, top_k: int = 6):
    if not result:
        return None

    scored = []
    for doc, meta in zip(result["documents"], result["metadatas"]):
        meta = safe_meta(meta)
        score = meta.get("fusion_score", 0) + rank_personal_fact_boost(meta)
        scored.append((score, doc, meta))

    scored.sort(key=lambda x: x[0], reverse=True)

    docs = [doc for _, doc, _ in scored[:top_k]]
    metas = [meta for _, _, meta in scored[:top_k]]
    return {"documents": docs, "metadatas": metas} if docs else None



def choose_merge_mode(category: str, question: str):
    if is_profile_summary_query(question):
        return "profile-summary"
    if is_personal_fact_query(question):
        return "personal-first"
    if is_list_query(question):
        return "project-website-first"
    if category in MANUAL_PRIORITY_CATEGORIES:
        return "manual-first"
    if category in SEMANTIC_PRIORITY_CATEGORIES:
        return "semantic-first"
    return "balanced"



def retrieve(question: str):
    total_start = perf_counter()
    print("=" * 70)
    print("Retrieving...")

    category = detect_category(question)
    merge_mode = choose_merge_mode(category, question)
    print("Detected Category :", category)
    print("Merge Mode       :", merge_mode)

    if merge_mode == "project-website-first":
        top_k = 24
    elif merge_mode == "profile-summary":
        top_k = 16
    else:
        top_k = 12

    category_result = None
    if category:
        category_result = category_search(category, question, top_k=top_k)
        if category_result is not None:
            print(f"Category returned {len(category_result['documents'])} doc(s)")
            for meta in category_result["metadatas"][:5]:
                print(f"CAT -> {meta.get('filename', '?')} | {meta.get('category', '?')} | {meta.get('source_type', '?')}")

    keyword_result = keyword_search(question, top_k=top_k)
    if keyword_result is not None:
        print(f"Keyword returned {len(keyword_result['documents'])} doc(s)")

    semantic_where = None
    if category == "projects":
        semantic_where = {"category": "projects"}
    elif category == "personal":
        semantic_where = {"category": "personal"}
    elif category == "profile":
        semantic_where = None
    elif category:
        semantic_where = {"category": category}

    semantic_result = semantic_search(question, top_k=top_k, where=semantic_where)
    if semantic_result is not None:
        print(f"Semantic returned {len(semantic_result['documents'])} doc(s)")

    fused = reciprocal_rank_fusion([
        ("category", category_result),
        ("keyword", keyword_result),
        ("semantic", semantic_result),
    ])

    if merge_mode == "project-website-first":
        filtered_docs = []
        filtered_metas = []
        if fused:
            for doc, meta in zip(fused["documents"], fused["metadatas"]):
                if meta.get("category") != "projects":
                    continue
                if is_home_meta(meta):
                    continue
                filtered_docs.append(doc)
                filtered_metas.append(meta)

        filtered = {"documents": filtered_docs, "metadatas": filtered_metas} if filtered_docs else None
        prioritized = prioritize_project_results(filtered, top_k=14)
        final_result = dedup_grouped_results(prioritized, top_k=12, by_project=True)
    elif merge_mode == "profile-summary":
        prioritized = prioritize_profile_summary_results(fused, top_k=10)
        final_result = dedup_grouped_results(prioritized, top_k=8, by_project=False)
    elif merge_mode == "personal-first":
        prioritized = prioritize_personal_fact_results(fused, top_k=8)
        final_result = dedup_grouped_results(prioritized, top_k=6, by_project=False)
    else:
        final_result = dedup_grouped_results(fused, top_k=8, by_project=False)

    print(f"Retriever : {perf_counter()-total_start:.3f}s")
    if final_result is None:
        print("No relevant document found.")
    else:
        print("Final merged docs:")
        for meta in final_result["metadatas"]:
            print(
                f"FINAL -> {meta.get('filename', '?')} | {meta.get('category', '?')} | "
                f"{meta.get('source_type', '?')} | score={meta.get('fusion_score', '-')} | "
                f"from={meta.get('fusion_sources', '-')}"
            )

    return final_result
