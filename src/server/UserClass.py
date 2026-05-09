class User:
    def __init__(self, nick, conexao_socket):
        self.nick = nick
        self.socket = conexao_socket
        self.inventario = {"trigo": 0, "arroz": 0, "cana": 0}
        # Aqui você pode colocar a cor do jogador no mapa, etc.
    
    def adiciona_item(self, item, quantidade=1):
        if item in self.inventario:
            self.inventario[item] += quantidade
    
    def remove_item(self, item, quantidade=1):
        if item in self.inventario and self.inventario[item] >= quantidade:
            self.inventario[item] -= quantidade

    def ver_inventario(self):
        return self.inventario
    
class GerenciadorUsers:
    def __init__(self):
        # Cria os 4 slots pré-alocados (em branco/None)
        self.slots = {
            1: None,
            2: None,
            3: None,
            4: None
        }

    def adiciona_na_vaga(self, conexao_socket):
        """Busca o primeiro slot vazio e aloca o novo jogador."""
        for id_slot, jogador in self.slots.items():
            if jogador is None:# Encontrou uma vaga!
                novo_jogador = User(nick=f"Jogador{id_slot}", conexao_socket=conexao_socket)
                self.slots[id_slot] = novo_jogador
                print(f"[+] Novo agricultor conectado! Slot {id_slot} ocupado.")
                return id_slot  # Retorna o ID para a thread de rede usar

        print("[-] Conexão recusada: A matriz já está lotada (4/4 jogadores).")
        return None  # Indica que não há vagas

    def remove_da_vaga(self, id_slot):
        """Libera o slot quando um jogador sai."""
        if id_slot in self.slots and self.slots[id_slot] is not None:
            self.slots[id_slot] = None
            print(f"[-] O jogador {id_slot} saiu. Slot {id_slot} liberado para novos acessos.")

    def exibir_jogadores_conectados(self):
        """Exibe os jogadores atualmente conectados."""
        print("Jogadores conectados:")
        for id_slot, jogador in self.slots.items():
            if jogador is not None:
                print(f" - Slot {id_slot}: {jogador.nick}")
            else:
                print(f" - Slot {id_slot}: Vazio")

#teste
if __name__ == "__main__":
    user1 = User(nick="Gabriel1", conexao_socket=None)
    user1.adiciona_item("trigo", 5)
    user1.adiciona_item("arroz", 3)
    print(user1.ver_inventario())  # {'trigo': 5, 'arroz': 3, 'cana': 0}
    
    user1.remove_item("trigo", 2)
    print(user1.ver_inventario())  # {'trigo': 3, 'arroz': 3, 'cana': 0}

    gerenciador = GerenciadorUsers()
    gerenciador.adiciona_na_vaga(conexao_socket="Socket1")  # Slot 1 ocupado
    gerenciador.adiciona_na_vaga(conexao_socket="Socket2")  # Slot 2 ocupado
    gerenciador.adiciona_na_vaga(conexao_socket="Socket3")  # Slot 3 ocupado
    gerenciador.adiciona_na_vaga(conexao_socket="Socket4")  # Slot 4 ocupado
    gerenciador.adiciona_na_vaga(conexao_socket="Socket5")  # Matriz lotada, conexão recusada
    gerenciador.remove_da_vaga(2)  # Slot 2 liberado
    gerenciador.remove_da_vaga(1)  # Slot 1 liberado
    gerenciador.adiciona_na_vaga(conexao_socket="Socket6")  # Slot 1 ocupado novamente
    gerenciador.exibir_jogadores_conectados()