from groq import Groq
from dotenv import load_dotenv

import os
import time

from builder.prompt import PromptBuilder
from builder.config import (
    TEMPERATURE,
    MAX_TOKENS
)

load_dotenv()


class KnowledgeBuilder:

    def __init__(self):

        self.client = Groq(

            api_key=os.getenv(

                "GROQ_API_KEY"

            )

        )

        self.prompt_builder = PromptBuilder()

        self.model = "llama-3.3-70b-versatile"

    # =====================================================
    # Generate Knowledge
    # =====================================================

    def generate(

        self,

        category,

        title,

        content,

        organization="",

        date=""

    ):

        prompt = self.prompt_builder.build(

            category=category,

            title=title,

            content=content,

            organization=organization,

            date=date

        )

        return self.generate_prompt(

            prompt

        )

    # =====================================================
    # Send Prompt
    # =====================================================

    def generate_prompt(

        self,

        prompt,

        retry=3

    ):

        for attempt in range(retry):

            try:

                response = self.client.chat.completions.create(

                    model=self.model,

                    temperature=TEMPERATURE,

                    max_tokens=MAX_TOKENS,

                    messages=[

                        {

                            "role": "system",

                            "content": (
                                "You are an expert Knowledge Engineer. "
                                "Your job is to transform resume sections "
                                "into structured knowledge documents. "
                                "Never invent information. "
                                "Use only the provided content."
                            )

                        },

                        {

                            "role": "user",

                            "content": prompt

                        }

                    ]

                )

                text = (

                    response

                    .choices[0]

                    .message

                    .content

                )

                if self.validate(text):

                    return text

                print()

                print("[WARNING] Invalid Knowledge Format")

                print()

            except Exception as e:

                print()

                print(f"[ERROR] Attempt {attempt+1}")

                print(e)

                print()

            time.sleep(2)

        raise Exception(

            "Knowledge Builder Failed."

        )

    # =====================================================
    # Validate Output
    # =====================================================

    def validate(

        self,

        text

    ):

        required = [

            "Category:",

            "Title:",

            "Summary:",

            "Responsibilities:",

            "Technologies:",

            "Keywords:",

            "Example Questions:",

            "Source:",

            "Confidence:"

        ]

        for field in required:

            if field not in text:

                return False

        return True