import json
import threading
import random

from ClassMapa import (TEMPO_CRESCIMENTO, MAPA_CRESCENDO_PARA_PRONTA,
                       MAPA_PRONTA_PARA_BASE, CULTURAS_PRONTAS, CULTURAS_CRESCENDO)
from ClassTemporada import Temporada, PRONTA_PARA_DEMANDA


class ControladorFazenda:
    """Responsável por traduzir JSONs e aplicar as regras de negócio do jogo."""

    def __init__(self, mapa_instancia, gerenciador_instancia, estoque_instancia):
        self.mapa = mapa_instancia
        self.gerenciador = gerenciador_instancia
        self.estoque = estoque_instancia
        self.temporada = None
        self._broadcast = None              # injetado via registrar_broadcast()
        self._timers_crescimento = {}       # {(x, y): threading.Timer}
        self._lock_timers = threading.Lock()

    def registrar_broadcast(self, fn_broadcast):
        """Injeta a função de broadcast do ServidorTCP."""
        self._broadcast = fn_broadcast

    def conecta_jogador(self):
        """Tenta achar um slot livre e retorna o ID (ou None se cheio)."""
        return self.gerenciador.adiciona_na_vaga()

    def desconecta_jogador(self, id_jogador):
        self.gerenciador.remove_da_vaga(id_jogador)

    def gera_boas_vindas(self, id_jogador):
        return json.dumps({"comando": "RESPOSTA", "status": "OK",
                           "mensagem": f"BEM_VINDO: Jogador {id_jogador}"}) + "\n"

    # -------------------------------------------------------------------------
    # Lógica de temporada
    # -------------------------------------------------------------------------

    def iniciar_temporada(self, numero: int):
        """Para a temporada atual (se houver) e inicia uma nova."""
        num_jogadores = sum(1 for v in self.gerenciador.slots.values() if v is not None)
        if self.temporada:
            self.temporada.parar()
        self.estoque.inicializar(numero)
        self.temporada = Temporada(
            numero=numero,
            num_jogadores=num_jogadores,
            ao_tick=self._ao_tick_temporada,
            ao_derrota=self._ao_derrota,
            ao_gelo=self._ao_gelo if numero >= 4 else None,
        )
        self.temporada.iniciar()
        estado = self.temporada.get_estado()
        msg = json.dumps({
            "comando": "INICIO_TEMPORADA",
            "numero": estado["numero"],
            "demanda": estado["demanda"],
            "restante": estado["restante"],
            "estoque": self.estoque.snapshot(),
        }) + "\n"
        if self._broadcast:
            self._broadcast(msg)
        print(f"[JOGO] Temporada {numero} iniciada.")

    def _ao_tick_temporada(self, restante: int):
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "TICK_TIMER", "restante": restante}) + "\n")

    def _ao_vitoria(self, numero_temporada: int):
        print(f"[JOGO] Vitória na temporada {numero_temporada}!")
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "VITORIA",
                                        "temporada": numero_temporada}) + "\n")
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero_temporada + 1))
        t.daemon = True
        t.start()

    def _ao_derrota(self):
        numero_atual = self.temporada.numero if self.temporada else 1
        print(f"[JOGO] Derrota na temporada {numero_atual}.")
        if self._broadcast:
            self._broadcast(json.dumps({"comando": "DERROTA",
                                        "temporada": numero_atual}) + "\n")
        t = threading.Timer(5.0, lambda: self.iniciar_temporada(numero_atual))
        t.daemon = True
        t.start()

    def _ao_gelo(self):
        """Escolhe uma célula plantada aleatória e avisa que vai gelar em 10s."""
        celulas = [
            (x, y)
            for x in range(self.mapa.linha)
            for y in range(self.mapa.coluna)
            if (self.mapa.matriz[x][y] in CULTURAS_PRONTAS or
                self.mapa.matriz[x][y] in CULTURAS_CRESCENDO)
        ]
        if not celulas:
            return
        x, y = random.choice(celulas)
        if self._broadcast:
            self._broadcast(json.dumps({
                "comando": "AVISO_GELO", "x": x, "y": y, "segundos": 10
            }) + "\n")
        t = threading.Timer(10.0, lambda: self._aplicar_gelo(x, y))
        t.daemon = True
        t.start()

    def _aplicar_gelo(self, x, y):
        """Destrói a cultura na posição (x, y) se ainda estiver lá."""
        with self._lock_timers:
            timer = self._timers_crescimento.pop((x, y), None)
        if timer:
            timer.cancel()
        # Re-lê o tile após cancelar o timer para evitar race condition
        tile = self.mapa.matriz[x][y]
        if tile not in CULTURAS_PRONTAS and tile not in CULTURAS_CRESCENDO:
            return
        if tile in MAPA_PRONTA_PARA_BASE:
            self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE[tile]
        elif tile in MAPA_CRESCENDO_PARA_PRONTA:
            pronta = MAPA_CRESCENDO_PARA_PRONTA[tile]
            self.mapa.matriz[x][y] = MAPA_PRONTA_PARA_BASE.get(pronta, 0)
        if self._broadcast:
            self._broadcast(json.dumps({
                "comando": "ATUALIZAR_CELULA", "x": x, "y": y,
                "valor": self.mapa.matriz[x][y]
            }) + "\n")

    # -------------------------------------------------------------------------
    # Timers de crescimento
    # -------------------------------------------------------------------------

    def _iniciar_timer_crescimento(self, x, y, cultura):
        tempo = TEMPO_CRESCIMENTO.get(cultura, 30)
        with self._lock_timers:
            timer_antigo = self._timers_crescimento.pop((x, y), None)
        if timer_antigo:
            timer_antigo.cancel()
        timer = threading.Timer(tempo, lambda: self._planta_maturou(x, y))
        timer.daemon = True
        with self._lock_timers:
            self._timers_crescimento[(x, y)] = timer
        timer.start()

    def _planta_maturou(self, x, y):
        with self._lock_timers:
            self._timers_crescimento.pop((x, y), None)
        if not self.mapa.maturar(x, y):
            return
        tile_pronto = self.mapa.matriz[x][y]
        if self._broadcast:
            self._broadcast(json.dumps({
                "comando": "CULTURA_PRONTA", "x": x, "y": y, "valor": tile_pronto
            }) + "\n")

    # -------------------------------------------------------------------------
    # Processamento de mensagens do cliente
    # -------------------------------------------------------------------------

    def processa_mensagem(self, id_jogador, mensagem_str):
        print(f"[JOGO] Comando do Jogador {id_jogador}: {mensagem_str}")
        try:
            dados = json.loads(mensagem_str)
        except json.JSONDecodeError:
            return json.dumps({"comando": "RESPOSTA", "status": "ERRO",
                               "mensagem": "JSON invalido"}) + "\n", None

        comando = str(dados.get("comando", "")).strip().upper()
        resposta = {}
        broadcast = None

        if comando == "NICKNAME":
            nome = dados.get("nome", "SemNome")
            self.gerenciador.slots[id_jogador].nick = nome
            resposta = {"comando": "RESPOSTA", "status": "OK",
                        "mensagem": f"Nickname: {nome}"}

        elif comando == "PREPARAR":
            x, y = dados.get("x"), dados.get("y")
            if self.mapa.preparar(x, y):
                novo_valor = self.mapa.matriz[x][y]
                broadcast = json.dumps({
                    "comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor
                }) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Solo preparado"}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Nao foi possivel preparar"}

        elif comando == "PEGAR_SEMENTE":
            cultura = dados.get("cultura")
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Jogador nao encontrado"}
            elif self.estoque.pegar(cultura):
                if jogador.semente_na_mao == cultura:
                    jogador.quantidade_na_mao += 1
                else:
                    # Devolve cultura anterior ao estoque se havia outra
                    if jogador.semente_na_mao is not None:
                        self.estoque.repor(jogador.semente_na_mao, jogador.quantidade_na_mao)
                    jogador.semente_na_mao = cultura
                    jogador.quantidade_na_mao = 1
                snap = self.estoque.snapshot()
                broadcast = json.dumps({"comando": "ATUALIZAR_ESTOQUE", "estoque": snap}) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK",
                            "mensagem": f"Semente {cultura} na mao",
                            "cultura": cultura, "quantidade": jogador.quantidade_na_mao}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Sem sementes desse tipo"}

        elif comando == "PLANTAR":
            semente = dados.get("semente")
            x, y = dados.get("x"), dados.get("y")
            jogador = self.gerenciador.slots.get(id_jogador)
            if jogador is None or jogador.semente_na_mao != semente:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Sem semente na mao"}
            elif self.mapa.plantar(x, y, semente):
                jogador.quantidade_na_mao -= 1
                qtd_restante = jogador.quantidade_na_mao
                if qtd_restante <= 0:
                    jogador.semente_na_mao = None
                    jogador.quantidade_na_mao = 0
                cultura_plantada = self.mapa.matriz[x][y]
                self._iniciar_timer_crescimento(x, y, cultura_plantada)
                broadcast = json.dumps({
                    "comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": cultura_plantada
                }) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Plantado",
                            "cultura": semente if qtd_restante > 0 else None,
                            "quantidade": qtd_restante}
            else:
                # Semente permanece na mão — tile incompatível ou não preparado
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Nao foi possivel plantar ai",
                            "cultura": jogador.semente_na_mao,
                            "quantidade": jogador.quantidade_na_mao}

        elif comando == "COLHER":
            x, y = dados.get("x"), dados.get("y")
            ok, tile_pronto = self.mapa.colher(x, y)
            if ok:
                novo_valor = self.mapa.matriz[x][y]
                cultura_demanda = PRONTA_PARA_DEMANDA.get(tile_pronto)
                if cultura_demanda:
                    self.estoque.repor(cultura_demanda)
                snap = self.estoque.snapshot()
                broadcast_celula = json.dumps({
                    "comando": "ATUALIZAR_CELULA", "x": x, "y": y, "valor": novo_valor
                }) + "\n"
                broadcast_estoque = json.dumps({
                    "comando": "ATUALIZAR_ESTOQUE", "estoque": snap
                }) + "\n"
                progresso_msg = ""
                if self.temporada:
                    vitoria = self.temporada.registrar_colheita(tile_pronto)
                    estado = self.temporada.get_estado()
                    progresso_msg = json.dumps({
                        "comando": "ATUALIZAR_PROGRESSO",
                        "progresso": estado["progresso"],
                        "demanda": estado["demanda"],
                    }) + "\n"
                    if vitoria:
                        numero = self.temporada.numero
                        self.temporada.parar()
                        self._ao_vitoria(numero)
                broadcast = broadcast_celula + broadcast_estoque + progresso_msg
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Colhido"}
            else:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Nao ha cultura pronta ai"}

        elif comando == "CURSOR":
            x, y = dados.get("x"), dados.get("y")
            if x is None or y is None:
                resposta = {"comando": "RESPOSTA", "status": "ERRO",
                            "mensagem": "Coordenadas invalidas"}
            else:
                jogador = self.gerenciador.slots.get(id_jogador)
                if jogador:
                    jogador.posicao = (x, y)
                nick = jogador.nick if jogador else "?"
                broadcast = json.dumps({
                    "comando": "POSICAO_JOGADOR", "id": id_jogador,
                    "nick": nick, "x": x, "y": y
                }) + "\n"
                resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Cursor atualizado"}

        elif comando == "MATRIZ":
            resposta = {"comando": "ATUALIZAR_MAPA", "matriz": self.mapa.matriz}

        elif comando == "CHAT":
            mensagem = dados.get("mensagem", "")
            nick = self.gerenciador.slots[id_jogador].nick
            broadcast = json.dumps({
                "comando": "CHAT", "autor": nick, "mensagem": mensagem
            }) + "\n"
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Chat enviado"}

        elif comando == "SAIR":
            resposta = {"comando": "RESPOSTA", "status": "OK", "mensagem": "Desconectando..."}

        else:
            resposta = {"comando": "RESPOSTA", "status": "ERRO",
                        "mensagem": "Comando desconhecido"}

        return json.dumps(resposta) + "\n", broadcast
