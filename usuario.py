from socket import *
import threading
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import datetime


class Usuario():

    def __init__(self, hostA, hostB, portaUsuarioA, portaUsuarioB):
        """
        Ele cria um thread para executar a GUI.
        
        :param hostA: O endereço IP do primeiro usuário
        :param hostB: O endereço IP do outro usuário
        :param portaUsuarioA: A porta que o usuário usará para receber a mensagem
        :param portaUsuarioB: A porta que o usuário usará para enviar para outro usuário
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
        Ele envia uma mensagem para o servidor e aguarda uma mensagem de confirmação do servidor
        
        :param mensagem: A mensagem a ser enviada
        """
        self.enviar(self.codificarMensagem("ack", mensagem))

    def decodeMensagem(self, mensagem):
        """
        Ele recebe uma mensagem, decodifica-a, divide-a em uma lista e retorna a lista.
        
        :param mensagem: a mensagem que foi enviada
        :return: a mensagem, o remetente, o destinatário e o tipo de mensagem.
        """
        sep = "|"
        mensagem = mensagem.decode()
        vetormensagem = mensagem.split(sep)
        return vetormensagem[0], vetormensagem[1], vetormensagem[2], vetormensagem[3]

    def Receber(self, cliente, endereco):
        """
        Ele recebe uma mensagem de um cliente, verifica se é um ack, e se não for, ele envia um ack e
        imprime a mensagem.
        
        :param cliente: O socket do cliente
        :param endereco: O endereço do cliente
        """

        tipo, nomeOrigem, tempo, mensagem = self.decodeMensagem(
            cliente.recv(1024))

        cliente.close()
        if tipo == "ack" and (mensagem in self.historicoMensagem):
            self.escrever(" «", 1)
            self.historicoMensagem.remove(mensagem)
        
        elif tipo == "post":
            self.ack(mensagem)
            mensagem = "\n {} {}: \n  {}".format(
                tempo, nomeOrigem, mensagem)
            self.escrever(mensagem)

    def Listing(self):
        """
        Ele cria um soquete, liga-o ao host e, em seguida, escuta as conexões.
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
        Retorna a hora atual no formato HH:MM:SS
        :return: A hora no formato HH:MM:SS
        """
        tempo = datetime.datetime.now()
        tempo = str(tempo.hour) + ":" + str(tempo.minute) + \
            ":" + str(tempo.second)
        return tempo

    def codificarMensagem(self, tipo, mensagem):
        """
        Ele pega uma mensagem e a codifica com um tipo, nome de usuário e carimbo de data/hora.
        
        :param tipo: tipo de mensagem
        :param mensagem: a mensagem a ser enviada
        :return: A mensagem está sendo codificada.
        """
        sep = "|"
        mensagem = tipo + sep + self.nomeUsuario + \
            sep + self.getTimeNow() + sep + mensagem
        return mensagem.encode()

    def enviar(self, mensagem):
        """
        Cria um socket, conecta-se ao servidor, envia a mensagem e fecha o socket
        
        :param mensagem: A mensagem a ser enviada
        """
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect(self.host[1])
            s.send(mensagem)
            s.close()
        except Exception as erro:
            messagebox.showerror("Erro", "Erro ao enviar. ERRO: " + str(erro))

    def escrever(self, mensagem, posicao=0):
        """
        Ele insere uma mensagem em uma caixa de texto
        
        :param mensagem: A mensagem a ser escrita
        :param posicao: 0 = anexar ao final da caixa de texto, 1 = inserir antes da última linha, padrão
        a 0 (opcional)
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
            Se o aplicativo não for iniciado, pergunte ao usuário seu nome, inicie o aplicativo, inicie
            o encadeamento, defina o título do aplicativo e escreva uma mensagem de boas-vindas.
            Se o aplicativo for iniciado, mostre uma mensagem de aviso.
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
            Se o aplicativo não for iniciado, pergunte ao usuário seu nome, inicie o aplicativo e defina
            o título do aplicativo.
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
portaUsuarioA = 4000
portaUsuarioB = 5000

Usuario(hostA, hostB, portaUsuarioA, portaUsuarioB)
