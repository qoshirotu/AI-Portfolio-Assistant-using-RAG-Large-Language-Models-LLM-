import re
from pathlib import Path


def clean_filename(text: str):

    text = text.lower()

    text = text.replace("&", "and")

    text = re.sub(r"[^a-z0-9 ]", "", text)

    text = text.strip()

    text = text.replace(" ", "_")

    return text


def ensure_directory(path: Path):

    path.mkdir(

        parents=True,

        exist_ok=True

    )


def save_text(path: Path, text: str):

    ensure_directory(

        path.parent

    )

    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(text)


def read_text(path: Path):

    with open(

        path,

        "r",

        encoding="utf-8"

    ) as f:

        return f.read()