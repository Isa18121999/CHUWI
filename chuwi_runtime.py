from chuwi_controller import ChuwiController
from chuwi_ui import ChuwiUI
from chuwi_face import ChuwiFace
from chuwi_ai_engine import ChuwiAIEngine
from chuwi_conversation import ChuwiConversation
from memory_manager import MemoryManager


class ChuwiRuntime:
    def __init__(self):
        self.controller = ChuwiController()
        self.ui = ChuwiUI()
        self.face = ChuwiFace()
        self.ai = ChuwiAIEngine()
        self.memory = MemoryManager()
        self.conversation = ChuwiConversation(
            memory=self.memory,
            ai_engine=self.ai
        )

    def update(self, distance):
        self.controller.update_distance(distance)
        state = self.controller.state.value

        self.ui.show_state(state)
        self.face.change_expression(state)

        return state

    def interact(self, message, context=None):
        context = context or self.ai.build_context(
            user_profile=self.memory.get_user(),
            conversation=self.memory.history
        )

        response = self.conversation.generate_response(
            message,
            context=context
        )

        return response
