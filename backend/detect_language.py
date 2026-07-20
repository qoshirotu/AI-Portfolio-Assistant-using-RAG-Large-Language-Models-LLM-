import re
from typing import List

ENGLISH_KEYWORDS = {
    "what", "who", "where", "when", "why", "which", "how", "tell", "describe", "explain",
    "introduce", "experience", "experiences", "project", "projects", "education", "skill", "skills",
    "contact", "email", "phone", "linkedin", "portfolio", "resume", "cv", "work", "internship",
    "university", "degree", "background", "about", "list", "show", "all", "can", "do", "does",
    "did", "is", "are", "was", "were", "have", "has", "job", "career", "research", "thesis"
}

INDONESIAN_KEYWORDS = {
    "apa", "siapa", "dimana", "di", "mana", "kapan", "mengapa", "kenapa", "bagaimana", "jelaskan",
    "ceritakan", "pengalaman", "proyek", "project", "pendidikan", "kuliah", "universitas", "keahlian",
    "kemampuan", "kontak", "email", "nomor", "telepon", "linkedin", "portofolio", "profil", "tentang",
    "daftar", "semua", "bisa", "apakah", "adalah", "pernah", "kerja", "pekerjaan", "magang", "skripsi"
}

ENGLISH_PHRASES = {
    "tell me", "show me", "who is", "what is", "where is", "how many", "list all", "all projects",
    "work experience", "contact information", "about qoshi", "is qoshi"
}

INDONESIAN_PHRASES = {
    "siapa qoshi", "apa itu", "apa saja", "semua projek", "semua proyek", "daftar proyek",
    "pengalaman kerja", "tentang qoshi", "siapa dia", "apakah qoshi"
}

ENGLISH_FUNCTION_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did", "to", "of", "for", "and",
    "or", "in", "on", "with", "from", "by", "at", "about", "me", "your", "his", "her"
}

INDONESIAN_FUNCTION_WORDS = {
    "yang", "dan", "atau", "di", "ke", "dari", "untuk", "pada", "dengan", "tentang", "itu", "ini",
    "saya", "aku", "dia", "kami", "kamu", "anda", "nya", "ada", "jadi", "dalam"
}

ENGLISH_STRONG_TOKENS = {"what", "who", "where", "when", "why", "which", "how", "is", "are", "tell", "show"}
INDONESIAN_STRONG_TOKENS = {"apa", "siapa", "dimana", "kapan", "kenapa", "mengapa", "bagaimana", "apakah", "jelaskan", "ceritakan"}

DEFAULT_LANGUAGE = "English"


def _normalize(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z']+", text)


def _count_matches(words: List[str], vocab: set) -> int:
    return sum(1 for word in words if word in vocab)


def _count_phrase_matches(text: str, phrases: set) -> int:
    return sum(1 for phrase in phrases if phrase in text)


def _has_indonesian_affixes(words: List[str]) -> bool:
    for word in words:
        if len(word) >= 5 and (
            word.startswith(("meng", "meny", "men", "mem", "ber", "ter", "per", "peng", "pem", "di"))
            or word.endswith(("kan", "nya", "lah", "kah", "pun", "i", "an"))
        ):
            return True
    return False


def _has_english_patterns(words: List[str]) -> bool:
    for word in words:
        if word.endswith(("ing", "tion", "ment", "ness", "ship", "able", "ize", "ise")):
            return True
    return False


def detect_language(question: str) -> str:
    text = _normalize(question)
    if not text:
        return DEFAULT_LANGUAGE

    words = _tokenize(text)
    if not words:
        return DEFAULT_LANGUAGE

    char_len = len(text)
    word_len = len(words)

    en_keyword = _count_matches(words, ENGLISH_KEYWORDS)
    id_keyword = _count_matches(words, INDONESIAN_KEYWORDS)
    en_func = _count_matches(words, ENGLISH_FUNCTION_WORDS)
    id_func = _count_matches(words, INDONESIAN_FUNCTION_WORDS)
    en_phrase = _count_phrase_matches(text, ENGLISH_PHRASES)
    id_phrase = _count_phrase_matches(text, INDONESIAN_PHRASES)
    en_strong = _count_matches(words, ENGLISH_STRONG_TOKENS)
    id_strong = _count_matches(words, INDONESIAN_STRONG_TOKENS)

    en_score = (en_keyword * 2) + en_func + (en_phrase * 3) + (en_strong * 2)
    id_score = (id_keyword * 2) + id_func + (id_phrase * 3) + (id_strong * 2)

    if _has_indonesian_affixes(words):
        id_score += 2
    if _has_english_patterns(words):
        en_score += 1

    if word_len <= 3 or char_len <= 18:
        if en_phrase > id_phrase:
            return "English"
        if id_phrase > en_phrase:
            return "Bahasa Indonesia"
        if en_strong > id_strong:
            return "English"
        if id_strong > en_strong:
            return "Bahasa Indonesia"
        if en_keyword > id_keyword:
            return "English"
        if id_keyword > en_keyword:
            return "Bahasa Indonesia"
        return DEFAULT_LANGUAGE

    if en_score > id_score:
        return "English"
    if id_score > en_score:
        return "Bahasa Indonesia"

    if any(word in {"the", "is", "are", "what", "who", "how"} for word in words):
        return "English"
    if any(word in {"yang", "apa", "siapa", "bagaimana", "apakah"} for word in words):
        return "Bahasa Indonesia"

    return DEFAULT_LANGUAGE
