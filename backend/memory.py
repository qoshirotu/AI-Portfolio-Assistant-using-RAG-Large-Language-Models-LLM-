from collections import deque


class ConversationMemory:

    def __init__(

        self,

        max_messages=10

    ):

        self.max_messages = max_messages

        self.messages = deque(

            maxlen=max_messages

        )

    # ==================================================

    def add_user(

        self,

        message

    ):

        self.messages.append(

            {

                "role": "user",

                "content": message

            }

        )

    # ==================================================

    def add_assistant(

        self,

        message

    ):

        self.messages.append(

            {

                "role": "assistant",

                "content": message

            }

        )

    # ==================================================

    def add(

        self,

        role,

        content

    ):

        self.messages.append(

            {

                "role": role,

                "content": content

            }

        )

    # ==================================================

    def history(self):

        return list(

            self.messages

        )

    # ==================================================

    def clear(self):

        self.messages.clear()

    # ==================================================

    def empty(self):

        return len(

            self.messages

        ) == 0

    # ==================================================

    def size(self):

        return len(

            self.messages

        )