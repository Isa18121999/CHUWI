from memory_manager import ChuwiMemory
from chuwi_emotional_manager import ChuwiEmotionalManager
from chuwi_ai_engine import ChuwiAIEngine


def run_tests():
    print("=== PRUEBAS CHUWI EMOTIONAL AI ===")

    memory = ChuwiMemory()
    emotional = ChuwiEmotionalManager()
    ai = ChuwiAIEngine()

    # Caso 1: memoria
    memory.save_user_name("Mateo")
    user = memory.get_user()
    assert user["name"] == "Mateo"
    print("OK - Memoria del paciente")

    # Caso 2: miedo a procedimiento médico
    result = emotional.analyze_interaction("Tengo miedo de mi operación")
    assert result["emotion"] in ["FEAR", "fear"]
    print("OK - Detección de miedo")

    response = ai.generate_response("Tengo miedo de mi operación", user)
    assert response is not None
    print("OK - Respuesta adaptativa")

    # Caso 3: tristeza
    result = emotional.analyze_interaction("Extraño mi casa y mi familia")
    assert result["emotion"] in ["SAD", "sad"]
    print("OK - Detección de tristeza")

    print("=== TODAS LAS PRUEBAS COMPLETADAS ===")


if __name__ == "__main__":
    run_tests()
