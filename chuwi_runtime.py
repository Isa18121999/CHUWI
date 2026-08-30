from chuwi_controller import ChuwiController
from chuwi_ui import ChuwiUI
from chuwi_face import ChuwiFace


class ChuwiRuntime:
    def __init__(self):
        self.controller = ChuwiController()
        self.ui = ChuwiUI()
        self.face = ChuwiFace()

    def update(self, distance):
        self.controller.update_distance(distance)
        state = self.controller.state.value

        self.ui.show_state(state)
        self.face.change_expression(state)

        return state
