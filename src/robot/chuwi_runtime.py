from src.robot.chuwi_controller import ChuwiController
from src.interface.chuwi_ui import ChuwiUI
from src.robot.chuwi_face import ChuwiFace
from src.core.chuwi_ai_engine import ChuwiAIEngine
from src.core.chuwi_conversation import ChuwiConversation
from src.memory.memory_manager import ChuwiMemory


class ChuwiRuntime:
    def __init__(self):
        self.controller = ChuwiController()
        self.ui = ChuwiUI()
        self.face = ChuwiFace()
        self.ai = ChuwiAIEngine()
        self.memory = ChuwiMemory()
        self.conversation = ChuwiConversation(memory=self.memory, ai_engine=self.ai)

    def update(self, distance):
        self.controller.update_distance(distance)
        state = self.controller.state.value
        self.ui.show_state(state)
        self.face.change_expression(state)
        return state

    def interact(self, message, context=None):
        if context is None:
            context = self.ai.build_context(
                user_profile=self.memory.get_user(),
                conversation=self.memory.history,
            )
        response = self.ai.generate_response(message, context)
        if isinstance(response, tuple):
            response = response[0]
        self.memory.remember(message)
        return response
