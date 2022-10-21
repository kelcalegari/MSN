from socket import *
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import datetime


class Usuario():

    def __init__(self, hostA, hostB, portaUsuarioA, portaUsuarioB):
        """
        It creates a thread to run the GUI.
        
        :param hostA: The IP address of the first user
        :param hostB: The IP address of the other user
        :param portaUsuarioA: The port that the user will use to receive the message
        :param portaUsuarioB: The port that the user will use to send to another user
        """

        self.hostA = (hostA, portaUsuarioA)
        self.hostB = (hostB, portaUsuarioB)
        self.host = []
        self.nomeUsuario = ""
        self.historicoMensagem = []
        # Criando um thread para executar a GUI.
        self.mutexMensagem = threading.Lock()
        threading.Thread(target=self.janela).start()

    def ack(self, mensagem):
        """
        It sends a message to the server, and then waits for an ack message from the server
        
        :param mensagem: The message to be sent
        """
        self.enviar(self.codificarMensagem("ack", mensagem))

    def decodeMensagem(self, mensagem):
        """
        It receives a message, decodes it, splits it into a list and returns the list.
        
        :param mensagem: the message that was sent
        :return: the message, the sender, the receiver and the message type.
        """
        sep = "|"
        mensagem = mensagem.decode()
        vetormensagem = mensagem.split(sep)
        return vetormensagem[0], vetormensagem[1], vetormensagem[2], vetormensagem[3]

    def Receber(self, cliente, endereco):
        """
        It receives a message from a client, checks if it's an ack, and if it's not, it sends an ack and
        prints the message.
        
        :param cliente: The client socket
        :param endereco: The address of the client
        """

        tipo, nomeOrigem, tempo, mensagem = self.decodeMensagem(
            cliente.recv(1024))

        cliente.close()
        if tipo == "ack" and (mensagem in self.historicoMensagem):
            self.escrever(" «", 1)
            self.historicoMensagem.remove(mensagem)

        else:
            self.ack(mensagem)
            mensagem = "\n {} {}: \n  {}".format(
                tempo, nomeOrigem, mensagem)
            self.escrever(mensagem)

    def Listing(self):
        """
        It creates a socket, binds it to the host, and then listens for connections.
        """

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
            messagebox.showerror(
                "Erro", "Selecione o usuario novamente. ERRO: " + str(erro))
            self.limparTela()
            self.iniciado = False

    def getTimeNow(self):
        """
        It returns the current time in the format of HH:MM:SS
        :return: The time in the format of HH:MM:SS
        """
        tempo = datetime.datetime.now()
        tempo = str(tempo.hour) + ":" + str(tempo.minute) + \
            ":" + str(tempo.second)
        return tempo

    def codificarMensagem(self, tipo, mensagem):
        """
        It takes a message and encodes it with a type, username, and timestamp.
        
        :param tipo: type of message
        :param mensagem: the message to be sent
        :return: The message is being encoded.
        """
        sep = "|"
        mensagem = tipo + sep + self.nomeUsuario + \
            sep + self.getTimeNow() + sep + mensagem
        return mensagem.encode()

    def enviar(self, mensagem):
        """
        It creates a socket, connects to the server, sends the message and closes the socket
        
        :param mensagem: The message to be sent
        """
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.connect(self.host[1])
            s.send(mensagem)
            s.close()
        except Exception as erro:
            messagebox.showerror("Erro", "Erro ao enviar. ERRO: " + str(erro))

    def escrever(self, mensagem, posicao=0):
        """
        It inserts a message into a textbox
        
        :param mensagem: The message to be written
        :param posicao: 0 = append to the end of the textbox, 1 = insert before the last line, defaults
        to 0 (optional)
        """
        
        self.mutexMensagem.acquire()
        if posicao == 0:
            self.mensagens.insert(END, mensagem)
        else:
            self.mensagens.insert("end-2line lineend", mensagem)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutexMensagem.release()

    def limparTela(self):
        # Excluindo o texto do widget de texto e reempacotando-o.
        self.mutexMensagem.acquire()
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
                if len(mensagem.get("1.0", END)) < 901:
                    if self.iniciado:
                        textoMensagens = str(mensagem.get("1.0", END))
                        try:
                            # Enviando a mensagem para o outro usuário, gravando a mensagem na GUI e
                            # em seguida, excluindo a mensagem do widget de texto.
                            self.enviar(self.codificarMensagem(
                                "post", textoMensagens))
                            self.historicoMensagem.append(textoMensagens)
                            textoMensagens = "\n " + self.getTimeNow() + " Você: \n  " + textoMensagens
                            self.escrever(textoMensagens)
                            mensagem.delete("1.0", END)
                        except Exception as erro:
                            messagebox.showerror(
                                "Erro enviar mensagem", "Mensagem não enviada. ERRO: " + str(erro))

                    else:
                        messagebox.showwarning(
                            "Aplicativo não iniciado!!", "Aplicativo não iniciado!! Selecione um Usuario. ")
                else:
                    messagebox.showwarning(
                        "Aviso!!", "Tamanho maximo atingido, max de 900 caracteres")
                    print(len(mensagem.get("1.0", END)))

        def usuarioA():
            """
            If the application is not started, ask the user for his name, start the application, start
            the thread, set the application title, and write a welcome message.
            If the application is started, show a warning message.
            """
            if self.iniciado == False:
                self.nomeUsuario = simpledialog.askstring(
                    title="Nome", prompt="Informe o seu nome:")
                self.host.clear()
                self.host.append(self.hostA)
                self.host.append(self.hostB)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - {}".format(self.nomeUsuario))
                self.escrever(
                    "\n Bem vindo {}, você iniciou como A!!\n".format(self.nomeUsuario))
            else:
                messagebox.showwarning(
                    "Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!")

        def usuarioB():
            """
            If the application is not started, ask the user for his name, start the application, and set
            the application title.
            """
            if self.iniciado == False:
                self.nomeUsuario = simpledialog.askstring(
                    title="Nome", prompt="Informe o seu nome:")
                self.host.clear()
                self.host.append(self.hostB)
                self.host.append(self.hostA)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - {}".format(self.nomeUsuario))
                self.escrever(
                    "\n Bem vindo {}, você iniciou como B!!\n".format(self.nomeUsuario))
            else:
                messagebox.showwarning(
                    "Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!")

        def fechar():
            app.destroy()

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

        Label(app, text="Informe a mensagem: (max: 900 char) ", background="#dde",
              foreground="#000", anchor="s").place(x=10, y=200, width=210, height=20)
        mensagem = Text(app)
        mensagem.place(x=10, y=220, width=425, height=80)

        Button(app, text="Enviar", command=buttonEnviar).place(
            x=440, y=220, width=50, height=80)
        app.mainloop()


# Criando um objeto de usuário
hostA = "localhost"
hostB = "localhost"
portaUsuarioA = 3535
portaUsuarioB = 5353

Usuario(hostA, hostB, portaUsuarioA, portaUsuarioB)
