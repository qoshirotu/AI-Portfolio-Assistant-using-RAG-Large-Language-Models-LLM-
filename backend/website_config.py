SITE_URL = "https://qoshi.framer.website"
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"

ALLOWED_PATH_KEYWORDS = [
    "/project",
    "/projects",
    "/experience",
    "/about",
    "/contact",
    "/research",
    "/work",
    "/portfolio",
]

BLOCKED_PATH_KEYWORDS = [
    "/404",
    "/terms",
    "/privacy",
    "/thank-you",
    "/legal",
    "/cookie",
]

REQUEST_TIMEOUT = 20
USER_AGENT = "QoshiBotSync/1.0 (+https://qoshi.framer.website)"
MAX_CHUNK_CHARS = 1000
CHUNK_OVERLAP = 120

SYNC_STATE_DIR = "app/sync_state"
SYNC_HASH_FILE = f"{SYNC_STATE_DIR}/website_hashes.json"
