class User:
    def __init__(self, nick):
        self.nick = nick
        self.semente_na_mao = None  # int ou None: cultura que o jogador pegou do estoque
        self.posicao = None          # (x, y) ou None: tile selecionado no mapa


class GerenciadorUsers:
    def __init__(self):
        self.slots = {1: None, 2: None, 3: None, 4: None}

    def adiciona_na_vaga(self):
        """Busca o primeiro slot vazio e aloca o novo jogador."""
        for id_slot, jogador in self.slots.items():
            if jogador is None:
                novo_jogador = User(nick=f"Jogador{id_slot}")
                self.slots[id_slot] = novo_jogador
                print(f"[+] Novo agricultor conectado! Slot {id_slot} ocupado.")
                return id_slot

        print("[-] Conexão recusada: A matriz já está lotada (4/4 jogadores).")
        return None

    def remove_da_vaga(self, id_slot):
        """Libera o slot quando um jogador sai."""
        if id_slot in self.slots and self.slots[id_slot] is not None:
            self.slots[id_slot] = None
            print(f"[-] O jogador {id_slot} saiu. Slot liberado.")

    def exibir_jogadores_conectados(self):
        print("Jogadores conectados:")
        for id_slot, jogador in self.slots.items():
            estado = jogador.nick if jogador is not None else "Vazio"
            print(f" - Slot {id_slot}: {estado}")


if __name__ == "__main__":
    g = GerenciadorUsers()
    id1 = g.adiciona_na_vaga()
    assert id1 == 1
    assert g.slots[1].semente_na_mao is None
    assert g.slots[1].posicao is None
    g.slots[1].semente_na_mao = 3
    assert g.slots[1].semente_na_mao == 3
    g.slots[1].posicao = (5, 7)
    assert g.slots[1].posicao == (5, 7)
    g.remove_da_vaga(id1)
    assert g.slots[1] is None
    print("ClassUser: todos os testes passaram.")
