from enum import Enum


class AffectiveState(Enum):
    IDLE = "idle"
    WELCOME = "welcome"
    LISTENING = "listening"
    THINKING = "thinking"
    HAPPY = "happy"
    CALM = "calm"
    SUPPORTIVE = "supportive"
    SLEEP = "sleep"


class ChuwiAffectiveOutput:
    """
    Output affective layer for Chuwi.

    Chuwi is a plush assistive robot without a screen or servomotors.
    Emotional expression is produced through voice style and interaction.
    """

    def __init__(self):
        self.state = AffectiveState.IDLE

    def set_state(self, state):
        self.state = state
        return self.state.value

    def get_voice_profile(self):
        profiles = {
            "idle": {
                "tone": "neutral",
                "speed": "normal"
            },
            "welcome": {
                "tone": "warm",
                "speed": "normal"
            },
            "listening": {
                "tone": "attentive",
                "speed": "slow"
            },
            "thinking": {
                "tone": "calm",
                "speed": "slow"
            },
            "happy": {
                "tone": "cheerful",
                "speed": "normal"
            },
            "calm": {
                "tone": "soft",
                "speed": "slow"
            },
            "supportive": {
                "tone": "empathetic",
                "speed": "slow"
            },
            "sleep": {
                "tone": "quiet",
                "speed": "slow"
            }
        }
        return profiles.get(self.state.value, profiles["idle"])
