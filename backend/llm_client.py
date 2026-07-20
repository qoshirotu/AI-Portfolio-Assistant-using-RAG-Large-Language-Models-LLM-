import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ======================================
# Provider
# ======================================

PROVIDER = "groq"
#PROVIDER = "gemini"
#PROVIDER = "qwen"
# PROVIDER = "openai"

# ======================================
# Model Configuration
# ======================================

MODELS = {

    "groq": "llama-3.1-8b-instant",

    "gemini": "gemini-3.5-flash",

    "deepseek": "deepseek-chat",

    "openai": "gpt-4.1-mini",

    "qwen" : "qwen3.5-flash"

}

# ======================================
# Client
# ======================================

if PROVIDER == "groq":

    client = OpenAI(

        api_key=os.getenv("GROQ_API_KEY"),

        base_url="https://api.groq.com/openai/v1"

    )

elif PROVIDER == "gemini":

    client = OpenAI(

        api_key=os.getenv("GEMINI_API_KEY"),

        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

    )

elif PROVIDER == "qwen":

    client = OpenAI(

        api_key=os.getenv("QWEN_API_KEY"),

        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    )

elif PROVIDER == "openai":

    client = OpenAI(

        api_key=os.getenv("OPENAI_API_KEY")

    )

else:

    raise ValueError(

        f"Unknown provider: {PROVIDER}"

    )

MODEL_NAME = MODELS[PROVIDER]

print("=" * 60)
print("Provider :", PROVIDER)
print("Model    :", MODEL_NAME)
print("=" * 60)
