class Message:
    def __init__(self, role, content) -> None:
        self.role = role
        self.content = content
        
class ChatSession:
    def __init__(self, id) -> None:
        self.id = id
        self.messages = []