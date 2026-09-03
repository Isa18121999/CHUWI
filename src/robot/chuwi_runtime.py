from src.robot.chuwi_controller import ChuwiController
from src.robot.chuwi_face import ChuwiAffectiveOutput
from src.core.chuwi_ai_engine import ChuwiAIEngine
from src.core.chuwi_conversation import ChuwiConversation
from src.memory.memory_manager import ChuwiMemory


class ChuwiRuntime:
    """
    Main runtime for Chuwi plush affective robot.

    Chuwi has no screen or servomotors. Emotional expression is performed
    through voice, conversation style and affective responses.
    """

    def __init__(self):
        self.controller = ChuwiController()
        self.affective_output = ChuwiAffectiveOutput()
        self.ai = ChuwiAIEngine()
        self.memory = ChuwiMemory()
        self.conversation = ChuwiConversation(
            memory=self.memory,
            ai_engine=self.ai,
        )

    def update(self, distance):
        self.controller.update_distance(distance)
        return self.controller.state.value

    def set_emotional_state(self, emotion):
        return self.affective_output.set_state(emotion)

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
