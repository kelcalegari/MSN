from socket import *
import threading
from time import sleep
from tkinter import *
from tkinter import messagebox
import sys

class Usuario():

    def __init__(self, hostA, hostB, portaUsuarioA, portaUsuarioB):


        self.hostA = (hostA, portaUsuarioA)
        self.hostB = (hostB, portaUsuarioB)
        self.host = []
        self.host.append(self.hostA)
        self.host.append(self.hostB)
        self.portaEnviar = 0
        
        # Criando um thread para executar a GUI.
        self.mutexMensagem = threading.Lock()
        threading.Thread(target=self.janela).start()
        

    def Receber(self, cliente, endereco):
        """
        Ele recebe uma mensagem de um cliente, decodifica, fecha a conexão e escreve a mensagem para
        a GUI.
        :param cliente: O socket do cliente
        :param endereco: O endereço IP e o número da porta do cliente
        """
        global mutex, historicoTemp
        mensagem = cliente.recv(8192)
        mensagem = mensagem.decode()
        
        cliente.close()
        mensagem = "\n IP: {}:{} \n  {}".format(
            endereco[0], endereco[1], mensagem)
        self.escrever(mensagem)

    def Listing(self):

        # Uma função que recebe uma mensagem de um cliente, a decodifica, fecha a conexão e
        # grava a mensagem na GUI.
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.bind(self.host[0])
            s.listen(10)

            while True:
                cliente, endereco = s.accept()
                
                threading.Thread(target=self.Receber,
                                args=(cliente, endereco)).start()
        except Exception as erro:
            messagebox.showerror("Erro", "Selecione o usuario novamente. ERRO: " + str(erro))
            self.limparTela()
            self.iniciado = False

    def enviar(self, mensagem):
        
        while True:
                
            try:
                # Binding the socket to the host and port of the user.
                enviarSocket = socket(AF_INET, SOCK_STREAM)
                enviarSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                enviarSocket.bind((self.host[0][0], self.portaEnviar))
                print(self.host[0][0], self.portaEnviar)
                break
            except OSError:
                self.portaEnviar +=1
                print("Erro", self.portaEnviar)
    
        try:
            # Criando um socket, configurando a opção socket para reutilizar o endereço, conectando ao
            # outro usuário, enviando a mensagem e fechando o soquete.
            
            enviarSocket.connect(self.host[1])
            enviarSocket.send(mensagem.encode())
            enviarSocket.close()
            
            
        
        except Exception as erro:
            
            messagebox.showerror("Erro", "Erro ao enviar. ERRO: " + str(erro))

    def escrever(self, mensagem):
        # Bloqueando a GUI para que apenas um thread possa gravar nela por vez.
        self.mutexMensagem.acquire()
        # Inserindo a mensagem no widget de texto, configurando a barra de rolagem e reempacotando
        # o widget de texto.
        self.mensagens.insert(END, mensagem)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutexMensagem.release()

    def limparTela(self):
        self.mutexMensagem.acquire()
        # Excluindo o texto do widget de texto e reempacotando-o.
        self.mensagens.delete("1.0", END)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutexMensagem.release()

    def janela(self):
        """
        Ele cria uma janela GUI com um widget de texto para as mensagens, um widget de texto para a mensagem a ser
        enviado e um botão para enviar a mensagem
        """
        self.iniciado = False
        app = Tk()
        app.title("MSN")
        app.geometry("500x310")
        app.configure(background="#dde")

        def buttonEnviar():

            if len(mensagem.get("1.0", END)) > 1:
                if self.iniciado:
                    textoMensagens = str(mensagem.get("1.0", END))
                    try:
                        # Enviando a mensagem para o outro usuário, gravando a mensagem na GUI e
                        # em seguida, excluindo a mensagem do widget de texto.
                        self.enviar(textoMensagens)
                        textoMensagens = "\n VOCÊ: \n  " + textoMensagens
                        self.escrever(textoMensagens)
                        mensagem.delete("1.0", END)
                    except Exception as erro:
                        messagebox.showerror("Erro enviar mensagem", "Mensagem não enviada. ERRO: " + str(erro))
                    
                    
                else:
                    messagebox.showwarning("Aplicativo não iniciado!!", "Aplicativo não iniciado!! Selecione um Usuario. " )
                    

        def usuarioA():
            """
            Função que é chamada quando o usuário clica no item de menu "Usuario A". Ele verifica
            para ver se o aplicativo já foi iniciado. Se não tiver, ele limpa o host
            list, ordena na ordem hostA e hostB à lista, inicia o thread de listagem, define o
            iniciada variável para True, define o título da janela GUI para "MSN - Usuario A", e
            grava uma mensagem na GUI.
            """
            if self.iniciado == False:
                self.host.clear()
                self.host.append(self.hostA)
                self.host.append(self.hostB)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - Usuario A")
                self.portaEnviar = self.host[0][1] + 1

                self.escrever("\n Aplicativo iniciado como usuario A!!\n")

            else:
                messagebox.showwarning("Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!" )

        def usuarioB():
            """
            Função que é chamada quando o usuário clica no item de menu "Usuario B". Ele verifica
            para ver se o aplicativo já foi iniciado. Se não tiver, ele limpa o host
            list, ordena na ordem hostB e hostA à lista, inicia o thread de listagem, define o
            iniciada variável para True, define o título da janela GUI para "MSN - Usuario B", e
            grava uma mensagem na GUI.
            """
            if self.iniciado == False:
                self.host.clear()
                self.host.append(self.hostB)
                self.host.append(self.hostA)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - Usuario B")
                self.portaEnviar = self.host[0][1] + 1
                        
                self.escrever("\n Aplicativo iniciado como usuario B!!\n")
            else:
                messagebox.showwarning("Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!" )

        

        def fechar():
            app.destroy()
            sys.exit()

        # Criando uma barra de menus com dois menus, um chamado "Usuarios" e outro chamado "Opções". o
        # O menu "Usuarios" tem dois itens de menu, "Usuario A" e "Usuario B". O menu "Opções" possui dois
        # itens do menu, "Limpar tela" e "Fechar".
        menubar = Menu(app)
        usuarioMenu = Menu(menubar)
        opcoesMenu = Menu(menubar)
        app.config(menu=menubar)
        menubar.add_cascade(label='Usuarios', menu=usuarioMenu)
        menubar.add_cascade(label='Opções', menu=opcoesMenu)
        usuarioMenu.add_command(label='Usuario A', command=usuarioA)
        usuarioMenu.add_command(label='Usuario B', command=usuarioB)
        opcoesMenu.add_command(label='Limpar tela', command=self.limparTela)
        opcoesMenu.add_command(label='Fechar', command=fechar)

        # Criando uma janela GUI com um widget de texto para as mensagens, um widget de texto para a mensagem
        # ser enviado, e um botão para enviar a mensagem.
        frameHistorico = Frame(app)
        frameHistorico.place(x=10, y=10, width=480, height=180)

        self.scrollbar = Scrollbar(frameHistorico, orient='vertical')
        self.scrollbar.place(x=10, y=10, width=480, height=180)

        self.mensagens = Text(
            frameHistorico, yscrollcommand=self.scrollbar.set)
        self.mensagens.pack()

        self.mensagens['yscrollcommand'] = self.scrollbar.set

        Label(app, text="Informe a mensagem: ", background="#dde",
              foreground="#000", anchor="s").place(x=10, y=200, width=130, height=20)
        mensagem = Text(app)
        mensagem.place(x=10, y=220, width=425, height=80)

        Button(app, text="Enviar", command=buttonEnviar).place(
            x=440, y=220, width=50, height=80)
        app.mainloop()


# Criando um objeto de usuário
hostA = "localhost"
hostB = "localhost"
portaUsuarioA = 50000
portaUsuarioB = 40000

Usuario(hostA, hostB, portaUsuarioA, portaUsuarioB)

