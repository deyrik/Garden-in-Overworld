class User:
    def __init__(self, nick):
        self.nick = nick
        self.inventario = {"trigo": 0, "arroz": 0, "cana": 0}
    
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
        self.slots = {1: None, 2: None, 3: None, 4: None}

    def adiciona_na_vaga(self):
        """Busca o primeiro slot vazio e aloca o novo jogador."""
        for id_slot, jogador in self.slots.items():
            if jogador is None:
                # Gera um nome temporário baseado no número da vaga
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