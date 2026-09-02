from src.memory.memory_manager import ChuwiMemory
from src.emotion.chuwi_emotional_manager import ChuwiEmotionalManager
from src.core.chuwi_ai_engine import ChuwiAIEngine


def run_tests():
    print("=== PRUEBAS CHUWI EMOTIONAL AI ===")

    memory = ChuwiMemory()
    emotional = ChuwiEmotionalManager()
    ai = ChuwiAIEngine()

    memory.save_user_name("Paciente")
    user = memory.get_user()
    assert user["name"] == "Paciente"
    print("OK - Memoria del paciente")

    result = emotional.analyze_interaction("Tengo miedo de mi operación")
    assert result["emotion"] in ["FEAR", "fear"]
    print("OK - Detección de miedo")

    response = ai.generate_response("Tengo miedo de mi operación", user)
    assert response is not None
    print("OK - Respuesta adaptativa")

    result = emotional.analyze_interaction("Extraño mi casa y mi familia")
    assert result["emotion"] in ["SAD", "sad"]
    print("OK - Detección de tristeza")

    print("=== TODAS LAS PRUEBAS COMPLETADAS ===")


if __name__ == "__main__":
    run_tests()
