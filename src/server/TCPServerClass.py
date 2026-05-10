import socket
import threading
import MapaClass as map
import UserClass as uc
import json
import time

#USA ESSA CLASSE AQUI PRA TESTAR NO MESMO ARQUIVO (so q ela fere o princ de responsa. unica)
#class TCPServerClass:
    # def __init__(self, host, port):# def __init__(self, host, port, mapa_instancia, gerenciador_instancia):
        # self.host = host
        # self.port = port
        # self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server_socket.bind((self.host, self.port))
       
        #DEIXAR ESSE:
        #self.gerenciador = gerenciador_instancia  # Gerenciador de jogadores (slots)
        #self.mapa = mapa_instancia  
        
        #RETIRARA ABAIXO: USAR SO EM TESTE
        # Instancia as regras de negócio
        #self.gerenciador = uc.GerenciadorUsers() # Gerenciador de jogadores (slots)
        #self.mapa = map.Mapa()                     # Sua matriz do terreno

class TCPServerClass:
    def __init__(self, host = "localhost", port = 12345, mapa_instancia: map.Mapa = None, gerenciador_instancia: uc.GerenciadorUsers = None):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
       
        self.gerenciador = gerenciador_instancia  # Gerenciador de jogadores (slots)
        self.mapa = mapa_instancia  


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

        elif comando == "MATRIZ":
            return comando, []  # O cliente só quer a matriz, sem argumentos
       
        elif comando == "SAIR":
            return comando, []
        
        else:
            return "DESCONHECIDO", []

    def comando_nickname(self, client_socket, id_jogador, gerenciador, argumentos):
        """Processa o comando NICKNAME e envia a resposta para o cliente."""
        try:
            nome = argumentos[0]                       # O nome é o primeiro argumento
            gerenciador.slots[id_jogador].nick = nome  # Atualiza o nickname no gerenciador
            resposta = json.dumps({"status": "OK", "mensagem": "Nickname atualizado"}) + "\n"
            client_socket.sendall(resposta.encode())
        except Exception as e:
            resposta = json.dumps({"status": "ERRO", "mensagem": f"Erro ao processar NICKNAME: {e}"}) + "\n"
            client_socket.sendall(resposta.encode())
            return resposta

    def comando_plantar(self, client_socket, argumentos):
        """Processa o comando PLANTAR e envia a resposta para o cliente."""
        try:
            semente, x, y = argumentos
            sucesso = self.mapa.plantar(x, y, semente)
            
            if sucesso:
                resposta = json.dumps({"status": "OK", "mensagem": "Semente plantada"}) + "\n"
                client_socket.sendall(resposta.encode())
            else:
                resposta = json.dumps({"status": "ERRO", "mensagem": "Nao foi possivel plantar ai"}) + "\n"
                client_socket.sendall(resposta.encode())
        except Exception as e:
            resposta = json.dumps({"status": "ERRO", "mensagem": f"Erro ao processar PLANTAR: {e}"}) + "\n"
            client_socket.sendall(resposta.encode())
            return resposta
        
    def comando_colher(self, client_socket, argumentos):
        """Processa o comando COLHER e envia a resposta para o cliente."""
        try:
            cultura, x, y = argumentos
            sucesso = self.mapa.colher(x, y, cultura)
            
            if sucesso:
                resposta = json.dumps({"status": "OK", "mensagem": "Cultura colhida"}) + "\n"
                client_socket.sendall(resposta.encode())
            else:
                resposta = json.dumps({"status": "ERRO", "mensagem": "Nao foi possivel colher ai"}) + "\n"
                client_socket.sendall(resposta.encode())
        except Exception as e:
            resposta = json.dumps({"status": "ERRO", "mensagem": f"Erro ao processar COLHER: {e}"}) + "\n"
            client_socket.sendall(resposta.encode())
            return resposta
        
    def comando_matriz(self, client_socket, id_jogador):
        """Envia a matriz completa de uma vez. O TCP e o Cliente lidam com o tamanho."""
        try:
            # Pega a matriz inteira (ex: 20x20, 100x100, não importa o tamanho)
            matriz_completa = self.mapa.matriz

            # Cria UM ÚNICO JSON gigante com toda a informação
            dados_json = {
                "comando": "ATUALIZAR_MAPA",
                "matriz": matriz_completa
            }
            
            # Converte para string e coloca apenas UM \n no final absoluto
            pacote_gigante = json.dumps(dados_json) + "\n"
            
            # Envia para o os jogador do socket .
            try:
                        # O sendall() vai fatiar e enviar os bytes todos de uma vez
                client_socket.sendall(pacote_gigante.encode())
                return pacote_gigante  # Retorna o JSON gigante para debug
            except Exception as e:
                print(f"Falha ao enviar mapa pro Jogador {id_jogador}: {e}")

        except Exception as e:
            resposta = json.dumps({"status": "ERRO", "mensagem": f"Erro ao enviar matriz: {e}"}) + "\n"
            client_socket.sendall(resposta.encode())
            return resposta

    def conversa_cliente(self, client_socket, id_jogador):
        """Thread individual para cada cliente conectado."""
        try:
            # Manda uma mensagem de boas-vindas com o ID do jogador

            resposta = json.dumps({"status": "OK", "mensagem": f"BEM_VINDO: Jogador {id_jogador}"}) + "\n"
            client_socket.sendall(resposta.encode())

            while True:
                dados = client_socket.recv(1024).decode() #mensagem recebida (de ate 1024 bytes)
                if not dados:
                    break # Cliente desconectou

                comando, argumentos = self.processa_mensagem_json(dados)

                if comando == "NICKNAME":
                    resposta = self.comando_nickname(client_socket, id_jogador, self.gerenciador, argumentos)

                elif comando == "PLANTAR":
                    resposta = self.comando_plantar(client_socket, argumentos)

                elif comando == "COLHER":
                    resposta = self.comando_colher(client_socket, argumentos)

                elif comando == "MATRIZ":
                    resposta = self.comando_matriz(client_socket, id_jogador)

                elif comando == "SAIR":
                    resposta = json.dumps({"status": "OK", "mensagem": "Desconectando..."}) + "\n"
                    client_socket.sendall(resposta.encode())
                    break        

                print(f"Comando do Jogador {id_jogador}: {dados}")

                # o que enviei para o cliente, para debug
                print(f"Resposta para Jogador {id_jogador}: {resposta}")

        except Exception as e:
            print(f"Erro na conexão do Jogador {id_jogador}: {e}")
        finally:
            # Quando o loop quebra (desconexão ou erro), limpamos a vaga
            client_socket.close()
            self.gerenciador.remove_da_vaga(id_jogador)

# === mainServer.py ===
if __name__ == "__main__":
    servidor = TCPServerClass("localhost", 12345)
    servidor.mapa.exibe_colorido()  # Exibe o mapa no console para teste
    servidor.start()