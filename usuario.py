from socket import *
import threading
from time import sleep
from tkinter import *
from tkinter import messagebox

class Usuario():

    def __init__(self, hostA, hostB, portaUsuarioA, portaUsuarioB):

        self.hostA = (hostA, portaUsuarioA)
        self.hostB = (hostB, portaUsuarioB)
        self.host = []
        self.host.append(self.hostA)
        self.host.append(self.hostB)

        self.mutexMensagem = threading.Lock()
        threading.Thread(target=self.janela).start()
        

    def Receber(self, cliente, endereco):
        global mutex, historicoTemp
        mensagem = cliente.recv(8192)
        mensagem = mensagem.decode()
        cliente.close()
        mensagem = "\n IP: {}:{} \n  {}".format(
            endereco[0], endereco[1], mensagem)
        self.escrever(mensagem)

    def Listing(self):

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
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            s.connect(self.host[1])
            s.send(mensagem.encode())
            s.close()
        except Exception as erro:
            messagebox.showerror("Erro", "Erro ao enviar. ERRO: " + str(erro))

    def escrever(self, mensagem):
        self.mutexMensagem.acquire()
        self.mensagens.insert(END, mensagem)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutexMensagem.release()

    def limparTela(self):
        self.mutexMensagem.acquire()
        self.mensagens.delete("1.0", END)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutexMensagem.release()

    def janela(self):
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
                        self.enviar(textoMensagens)
                        textoMensagens = "\n VOCÊ: \n  " + textoMensagens
                        self.escrever(textoMensagens)
                        mensagem.delete("1.0", END)
                    except Exception as erro:
                        messagebox.showerror("Erro enviar mensagem", "Mensagem não enviada. ERRO: " + str(erro))
                    
                    
                else:
                    messagebox.showwarning("Aplicativo não iniciado!!", "Aplicativo não iniciado!! Selecione um Usuario. " )
                    

        def usuarioA():
            if self.iniciado == False:
                self.host.clear()
                self.host.append(self.hostA)
                self.host.append(self.hostB)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - Usuario A")
                self.escrever("\n Aplicativo iniciado como usuario A!!\n")

            else:
                messagebox.showwarning("Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!" )

        def usuarioB():
            if self.iniciado == False:
                self.host.clear()
                self.host.append(self.hostB)
                self.host.append(self.hostA)
                threading.Thread(target=self.Listing).start()
                self.iniciado = True
                app.title("MSN - Usuario B")
                self.escrever("\n Aplicativo iniciado como usuario B!!\n")
            else:
                messagebox.showwarning("Aviso", "Aplicativo já iniciado, para mudar o usuario feche e abre novamente!" )

        

        def fechar():
            app.destroy()

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


hostA = "localhost"
hostB = "localhost"
portaUsuarioA = 3535
portaUsuarioB = 5353

Usuario(hostA, hostB, portaUsuarioA, portaUsuarioB)
