class ChuwiMemory:

    def __init__(self):
        self.user = {
            "name": None,
            "age": None,
            "interests": [],
            "history": []
        }

    def save_user_name(self, name):
        self.user["name"] = name

    def remember(self, conversation):
        self.user["history"].append(conversation)

    def get_user(self):
        return self.user
