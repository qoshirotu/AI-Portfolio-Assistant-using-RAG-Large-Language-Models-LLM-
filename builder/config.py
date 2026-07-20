from pathlib import Path

# ===========================
# BASE DIRECTORY
# ===========================

BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================
# KNOWLEDGE DIRECTORY
# ===========================

KNOWLEDGE_DIR = BASE_DIR / "knowledge"

# ===========================
# TEMPLATE DIRECTORY
# ===========================

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

# ===========================
# OUTPUT
# ===========================

OUTPUT_ENCODING = "utf-8"

# ===========================
# LLM
# ===========================

TEMPERATURE = 0.1

MAX_TOKENS = 4096

# ===========================
# Supported Categories
# ===========================

SUPPORTED_CATEGORIES = [

    "profile",

    "education",

    "experience",

    "projects",

    "skills",

    "certifications",

    "contact"

]