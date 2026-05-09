import socket
import threading
import MapaClass as map
import UserClass as user
import json
import time


#Na instancia de TCPServerClass, o mapa e o gerenciador de jogadores são criados dentro do próprio servidor.
#Tirar e colocar o instaciamento na main, esta aqui apaneas para teste.


class TCPServerClass:
    def __init__(self, host, port):# def __init__(self, host, port, mapa_instancia, gerenciador_instancia):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
       
        #DEIXAR ESSE:
        #self.gerenciador = gerenciador_instancia  # Gerenciador de jogadores (slots)
        #self.mapa = mapa_instancia  
        
        #RETIRARA ABAIXO: USAR SO EM TESTE
        # Instancia as regras de negócio
        self.gerenciador = user.GerenciadorUsers() # Gerenciador de jogadores (slots)
        self.mapa = map.Mapa()                     # Sua matriz do terreno

    def start(self):
        """Inicia o servidor TCP e aguarda conexões de clientes.
        Para cada cliente, cria uma thread para tratar a comunicação."""

        self.server_socket.listen(4) # Prepara o SO para enfileirar até 4 conexões
        print(f"Servidor escutando em {self.host}:{self.port}...")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Tentativa de conexão de {addr}")

            # Tenta encaixar o cliente em um dos 4 slots
            id_alocado = self.gerenciador.adiciona_na_vaga(client_socket)

            if id_alocado is not None:
                # Se conseguiu vaga, cria a thread passando o ID dele
                client_thread = threading.Thread(target=self.conversa_cliente, args=(client_socket, id_alocado))
                client_thread.start()
            else:
                # Se os 4 slots estão cheios, avisa e fecha o socket na cara
                client_socket.sendall(b"ERRO: Servidor cheio.")
                client_socket.close()

    def processa_mensagem_json(self, mensagem):
        """
        Lê uma string JSON, classifica o comando e extrai os argumentos.
        Retorna uma tupla: (COMANDO, [lista_de_argumentos])
        """
        try:
            # Transforma a string recebida (JSON) em um Dicionário Python
            dados = json.loads(mensagem.strip())
        except json.JSONDecodeError:
            # Se o cliente mandar um texto bagunçado que não seja JSON, a gente bloqueia aqui
            return "ERRO", ["Mensagem não está no formato JSON válido"]

        # Extrai o comando usando .get() para evitar o erro de chave inexistente (KeyError)
        comando = str(dados.get("comando", "")).strip().upper()

        if comando == "NICKNAME":
            nome = dados.get("nome", "SemNome")
            return comando, [nome]
            
        elif comando == "PLANTAR":
            try:
                # Pegamos as chaves diretamente. Se faltar alguma, cai no except KeyError
                semente = int(dados["semente"])
                x = int(dados["x"])
                y = int(dados["y"])
                return comando, [semente, x, y]
            except KeyError:
                return "ERRO", ["Chaves faltando para PLANTAR (precisa de 'semente', 'x', 'y')"]
            except ValueError:
                return "ERRO", ["Os valores de semente, x e y devem ser números inteiros"]

        elif comando == "COLHER":
            try:
                cultura = int(dados["cultura"])
                x = int(dados["x"])
                y = int(dados["y"])
                return comando, [cultura, x, y]
            except KeyError:
                return "ERRO", ["Chaves faltando para COLHER (precisa de 'cultura', 'x', 'y')"]
            except ValueError:
                return "ERRO", ["Os valores de cultura, x e y devem ser inteiros"]

        elif comando == "SAIR":
            return comando, []

        else:
            return "DESCONHECIDO", []

    def conversa_cliente(self, client_socket, id_jogador):
        """Thread individual para cada cliente conectado."""
        try:
            # Manda uma mensagem de boas-vindas com o ID do jogador

            resposta = json.dumps({"status": "OK", "mensagem": f"BEM_VINDO: Jogador {id_jogador}"})
            client_socket.sendall(resposta.encode())

            while True:
                dados = client_socket.recv(1024).decode() #mensagem recebida (de ate 1024 bytes)
                if not dados:
                    break # Cliente desconectou

                comando, argumentos = self.processa_mensagem_json(dados)

                if comando == "NICKNAME":
                    nome = argumentos[0] 
                    self.gerenciador.slots[id_jogador].nick = nome
                    resposta = json.dumps({"status": "OK", "mensagem": "Nickname atualizado"})
                    client_socket.sendall(resposta.encode())

                elif comando == "PLANTAR":
                    # Como sabemos que PLANTAR devolve 3 argumentos [semente, x, y]
                    semente, x, y = argumentos
                    
                    # Chama a função da sua matriz!
                    sucesso = self.mapa.plantar(x, y, semente)
                    
                    if sucesso:
                        resposta = json.dumps({"status": "OK", "mensagem": "Semente plantada"})
                        client_socket.sendall(resposta.encode())
                    else:
                        resposta = json.dumps({"status": "ERRO", "mensagem": "Nao foi possivel plantar ai"})
                        client_socket.sendall(resposta.encode())

                elif comando == "COLHER":
                    cultura, x, y = argumentos

                    sucesso = self.mapa.colher(x, y, cultura)
                    
                    if sucesso:
                        resposta = json.dumps({"status": "OK", "mensagem": "Cultura colhida"})
                        client_socket.sendall(resposta.encode())
                    else:
                        resposta = json.dumps({"status": "ERRO", "mensagem": "Nao foi possivel colher ai"})
                        client_socket.sendall(resposta.encode())

                elif comando == "SAIR":
                    resposta = json.dumps({"status": "OK", "mensagem": "Desconectando..."})
                    client_socket.sendall(resposta.encode())
                    break        

                print(f"Comando do Jogador {id_jogador}: {dados}")
                
        except Exception as e:
            print(f"Erro na conexão do Jogador {id_jogador}: {e}")
        finally:
            # Quando o loop quebra (desconexão ou erro), limpamos a vaga
            client_socket.close()
            self.gerenciador.remove_da_vaga(id_jogador)

# === mainServer.py ===
if __name__ == "__main__":
    servidor = TCPServerClass("localhost", 12345)
    servidor.start()