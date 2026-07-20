from builder.config import TEMPLATE_DIR


class PromptBuilder:

    def __init__(self):

        self.template = self.load_template()

    # =====================================================

    def load_template(self):

        path = TEMPLATE_DIR / "rag_prompt.txt"

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as f:

            return f.read()

    # =====================================================

    def build(

        self,

        category,

        title,

        content,

        organization="",

        date=""

    ):

        prompt = self.template

        prompt = prompt.replace(

            "{category}",

            category

        )

        prompt = prompt.replace(

            "{title}",

            title

        )

        prompt = prompt.replace(

            "{organization}",

            organization

        )

        prompt = prompt.replace(

            "{date}",

            date

        )

        prompt = prompt.replace(

            "{content}",

            content.strip()

        )

        return prompt