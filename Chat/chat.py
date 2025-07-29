class Message:
    def __init__(self, role, message) -> None:
        self.role = role
        self.message = message
        
class ChatSession:
    def __init__(self, id) -> None:
        self.id = id
        self.messages = []