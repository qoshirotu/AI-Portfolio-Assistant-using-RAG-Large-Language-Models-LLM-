class ConversationBuilder:

    def __init__(

        self,

        max_history=3

    ):

        self.max_history = max_history

    # ==================================================

    def build(

        self,

        history

    ):

        if not history:

            return ""

        text = []

        text.append(

            "# CONVERSATION HISTORY\n"

        )

        recent = history[-self.max_history:]

        for item in recent:

            role = item["role"]

            content = item["content"]

            if role == "user":

                text.append(

                    f"User: {content}"

                )

            else:

                text.append(

                    f"Qoshi AI: {content}"

                )

        return "\n".join(

            text

        ).strip()


conversation_builder = ConversationBuilder()