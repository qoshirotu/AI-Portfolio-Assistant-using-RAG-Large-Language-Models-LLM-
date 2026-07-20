import uuid

from app.memory import ConversationMemory


class SessionManager:

    def __init__(self):

        self.sessions = {}

    # ==================================================

    def create(self):

        session_id = str(

            uuid.uuid4()

        )

        self.sessions[session_id] = (

            ConversationMemory()

        )

        return session_id

    # ==================================================

    def get(

        self,

        session_id

    ):

        if session_id not in self.sessions:

            self.sessions[session_id] = (

                ConversationMemory()

            )

        return self.sessions[session_id]

    # ==================================================

    def remove(

        self,

        session_id

    ):

        if session_id in self.sessions:

            del self.sessions[session_id]

    # ==================================================

    def clear_all(self):

        self.sessions.clear()


session_manager = SessionManager()