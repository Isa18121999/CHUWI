class ChuwiMemory:
    """Memoria de sesión y perfil básico del usuario."""

    def __init__(self):
        self.user = {
            "name": None,
            "age": None,
            "interests": [],
            "history": [],
        }

    @property
    def history(self):
        return self.user["history"]

    def save_user_name(self, name):
        self.user["name"] = name

    def remember(self, conversation):
        self.user["history"].append(conversation)

    def get_user(self):
        return self.user


# Alias compatible con versiones anteriores del runtime.
MemoryManager = ChuwiMemory
