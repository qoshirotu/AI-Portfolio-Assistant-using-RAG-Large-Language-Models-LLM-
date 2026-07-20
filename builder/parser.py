import re

class KnowledgeParser:
    """
    Parse LLM output into a structured Python dictionary.
    """

    def __init__(self):

        self.fields = [

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

    # =====================================================

    def parse(self, text: str):

        result = {}

        current_field = None

        buffer = []

        lines = text.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            matched = False

            for field in self.fields:

                if line.startswith(field + ":"):

                    # simpan field sebelumnya
                    if current_field is not None:

                        result[current_field] = "\n".join(
                            buffer
                        ).strip()

                    current_field = field

                    value = line.replace(
                        field + ":",
                        ""
                    ).strip()

                    buffer = []

                    if value:

                        buffer.append(value)

                    matched = True

                    break

            if not matched:

                if current_field:

                    buffer.append(line)

        # simpan field terakhir
        if current_field:

            result[current_field] = "\n".join(
                buffer
            ).strip()

        # isi field yang kosong
        for field in self.fields:

            if field not in result:

                result[field] = ""

        return result

    # =====================================================

    def validate(self, data):

        """
        Validate required fields.
        """

        required = [

            "Category",

            "Title",

            "Summary"

        ]

        for field in required:

            if field not in data:

                return False

            if len(data[field].strip()) == 0:

                return False

        return True

    # =====================================================

    def pretty_print(self, data):

        print()

        print("=" * 70)

        print("Parsed Knowledge")

        print("=" * 70)

        for key in self.fields:

            print(f"\n{key}")

            print("-" * 40)

            print(data.get(key, ""))

        print("\n" + "=" * 70)

    # =====================================================

    def to_text(self, data):

        """
        Convert dictionary back into structured text.
        """

        text = ""

        for field in self.fields:

            text += f"{field}:\n"

            text += data.get(field, "")

            text += "\n\n"

        return text.strip()