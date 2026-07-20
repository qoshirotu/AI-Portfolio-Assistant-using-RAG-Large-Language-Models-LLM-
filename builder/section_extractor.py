import json

from app.llm_client import (
    client,
    MODEL_NAME
)


class SectionExtractor:

    def __init__(self):

        with open(

            "builder/templates/section_prompt.txt",

            "r",

            encoding="utf-8"

        ) as f:

            self.prompt = f.read()

    # ======================================================

    def extract(self, resume):

        prompt = self.prompt.replace(

            "{{RESUME}}",

            resume

        )

        response = client.chat.completions.create(

            model=MODEL_NAME,

            temperature=0,

            response_format={"type": "json_object"},

            messages=[

                {

                    "role": "system",

                    "content": (
                        "You are an expert resume parser. "
                        "Always return valid JSON."
                    )

                },

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

        content = response.choices[0].message.content

        data = json.loads(content)

        return self.validate(data)

    # ======================================================

    def validate(self, data):

        default = {

            "profile": "",

            "education": "",

            "skills": "",

            "certifications": "",

            "contact": "",

            "experience": [],

            "projects": []

        }

        for key, value in default.items():

            if key not in data:

                data[key] = value

        # ------------------------
        # Experience
        # ------------------------

        cleaned_exp = []

        for item in data["experience"]:

            cleaned_exp.append(

                {

                    "title": item.get("title", ""),

                    "organization": item.get(

                        "organization",

                        ""

                    ),

                    "date": item.get(

                        "date",

                        ""

                    ),

                    "content": item.get(

                        "content",

                        ""

                    )

                }

            )

        data["experience"] = cleaned_exp

        # ------------------------
        # Projects
        # ------------------------

        cleaned_project = []

        for item in data["projects"]:

            cleaned_project.append(

                {

                    "title": item.get(

                        "title",

                        ""

                    ),

                    "content": item.get(

                        "content",

                        ""

                    )

                }

            )

        data["projects"] = cleaned_project

        return data