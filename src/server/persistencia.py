# src/server/persistencia.py
import sqlite3
import threading
import datetime


class BancoDados:
    """Persistência mínima em SQLite. Guarda apenas o histórico de chat.

    Thread-safe: a mesma conexão é usada por várias threads do servidor
    (worker de notificação, threads que atendem chamadas Pyro), por isso
    check_same_thread=False + lock próprio.
    """

    def __init__(self, caminho="garden.db"):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(caminho, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS chat ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "autor TEXT NOT NULL, "
            "mensagem TEXT NOT NULL, "
            "ts TEXT NOT NULL)"
        )
        self._conn.commit()

    def inserir_chat(self, autor, mensagem):
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        with self._lock:
            self._conn.execute(
                "INSERT INTO chat (autor, mensagem, ts) VALUES (?, ?, ?)",
                (autor, mensagem, ts),
            )
            self._conn.commit()

    def ultimas_mensagens(self, limite=50):
        """Retorna [(autor, mensagem), ...] em ordem cronológica (mais antiga primeiro)."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT autor, mensagem FROM chat ORDER BY id DESC LIMIT ?",
                (limite,),
            )
            linhas = cur.fetchall()
        return [(autor, msg) for autor, msg in reversed(linhas)]
