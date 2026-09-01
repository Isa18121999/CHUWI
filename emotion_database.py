import sqlite3


class EmotionDatabase:
    """Base de datos local de emociones y estrategias de apoyo de Chuwi."""

    def __init__(self, db_name="chuwi_emotions.sqlite"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()
        self.seed_emotions()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emotion TEXT NOT NULL,
            context TEXT,
            strategy TEXT
        )
        """)
        self.connection.commit()

    def seed_emotions(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM emotions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO emotions (emotion, context, strategy) VALUES (?, ?, ?)",
                [
                    ("fear", "procedimiento médico", "acompañamiento y calma"),
                    ("anxiety", "hospitalización", "respiración y conversación tranquila"),
                    ("sad", "separación familiar", "escucha activa y apoyo"),
                    ("frustrated", "dolor o dificultad", "motivación y distracción"),
                    ("happy", "interacción positiva", "refuerzo emocional")
                ]
            )
            self.connection.commit()

    def get_strategy(self, emotion):
        cursor = self.connection.cursor()
        cursor.execute("SELECT strategy FROM emotions WHERE emotion=?", (emotion,))
        result = cursor.fetchone()
        return result[0] if result else "acompañamiento general"
