import json

from pathlib import Path
from datetime import datetime

from builder.config import (
    KNOWLEDGE_DIR,
    OUTPUT_ENCODING
)

from builder.utils import (
    clean_filename,
    ensure_directory
)


class KnowledgeWriter:

    def __init__(self):

        self.base_dir = KNOWLEDGE_DIR

    # ====================================================

    def save(self, knowledge):

        self.validate(knowledge)

        category = knowledge["Category"].strip().lower()

        title = knowledge["Title"].strip()

        filename = clean_filename(title)

        category_dir = self.base_dir / category

        ensure_directory(category_dir)

        txt_path = category_dir / f"{filename}.txt"

        json_path = category_dir / f"{filename}.json"

        self.write_txt(

            txt_path,

            knowledge

        )

        self.write_json(

            json_path,

            knowledge,

            filename

        )

        return {

            "txt": txt_path,

            "json": json_path

        }

    # ====================================================

    def validate(self, knowledge):

        required = [

            "Category",

            "Title",

            "Summary",

            "Responsibilities",

            "Achievements",

            "Technologies",

            "Skills Demonstrated",

            "Keywords",

            "Example Questions",

            "Source",

            "Confidence"

        ]

        for field in required:

            if field not in knowledge:

                raise Exception(

                    f"Missing field : {field}"

                )

    # ====================================================

    def write_txt(

        self,

        path,

        knowledge

    ):

        text = self.build_txt(

            knowledge

        )

        with open(

            path,

            "w",

            encoding=OUTPUT_ENCODING

        ) as f:

            f.write(text)

    # ====================================================

    def write_json(

        self,

        path,

        knowledge,

        filename

    ):

        now = datetime.utcnow().isoformat()

        metadata = {

            "id": filename,

            "category": knowledge["Category"],

            "title": knowledge["Title"],

            "source": knowledge["Source"],

            "confidence": knowledge["Confidence"],

            "version": "2.0",

            "language": "en",

            "created_at": now,

            "updated_at": now

        }

        # optional metadata

        if "Organization" in knowledge:

            metadata["organization"] = knowledge["Organization"]

        if "Date" in knowledge:

            metadata["date"] = knowledge["Date"]

        data = {

            "metadata": metadata,

            "content": knowledge,

            "embedding": {

                "model": "BAAI/bge-m3",

                "chunk": 1,

                "chunk_size": "full_document"

            }

        }

        with open(

            path,

            "w",

            encoding=OUTPUT_ENCODING

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

                ensure_ascii=False

            )

    # ====================================================

    def build_txt(

        self,

        knowledge

    ):

        sections = [

            ("Category", knowledge["Category"]),

            ("Title", knowledge["Title"])

        ]

        if knowledge.get("Organization"):

            sections.append(

                ("Organization", knowledge["Organization"])

            )

        if knowledge.get("Date"):

            sections.append(

                ("Date", knowledge["Date"])

            )

        sections.extend([

            ("Summary", knowledge["Summary"]),

            ("Responsibilities", knowledge["Responsibilities"]),

            ("Achievements", knowledge["Achievements"]),

            ("Technologies", knowledge["Technologies"]),

            ("Skills Demonstrated", knowledge["Skills Demonstrated"]),

            ("Keywords", knowledge["Keywords"]),

            ("Example Questions", knowledge["Example Questions"]),

            ("Source", knowledge["Source"]),

            ("Confidence", knowledge["Confidence"])

        ])

        lines = []

        for key, value in sections:

            lines.append(f"{key}:")

            lines.append(str(value))

            lines.append("")

        return "\n".join(lines).strip()