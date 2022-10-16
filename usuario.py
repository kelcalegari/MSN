from socket import *
import threading
from time import sleep
from tkinter import *

class Usuario():
    
    def __init__(self,hostA,hostB,portaUsuarioA,portaUsuarioB):
        self.hostA = hostA
        self.hostB = hostB
        self.portaUsuarioA = portaUsuarioA
        self.portaUsuarioB = portaUsuarioB
        self.mutex = threading.Lock()
        threading.Thread( target = self.Listing).start()
        threading.Thread( target = self.janela).start()

    def Receber(self,cliente, endereco):
        global mutex, historicoTemp
        mensagem = cliente.recv(8192)
        mensagem = mensagem.decode()
        cliente.close()
        mensagem = "\n IP: {}:{} \n  {}".format(endereco[0], endereco[1],mensagem)
        self.escrever(mensagem)
    

    def Listing(self):

        s = socket(AF_INET, SOCK_STREAM)

        s.bind((self.hostA, self.portaUsuarioA))
        s.listen(10)

        while True:
            cliente, endereco = s.accept()
            threading.Thread( target = self.Receber, args = (cliente, endereco)).start()
        

    def enviar(self, mensagem):
        s = socket(AF_INET, SOCK_STREAM)
    
        s.connect((self.hostB, self.portaUsuarioB))  
        s.send(mensagem.encode()) 
        s.close()

    def escrever(self, mensagem):
        self.mutex.acquire()
        self.mensagens.insert(END, mensagem)
        self.scrollbar.config(command=self.mensagens.yview)
        self.mensagens.pack()
        self.mutex.release()



    def janela(self):

        app=Tk()
        app.title("MSN")
        app.geometry("500x310")
        app.configure(background="#dde")

        def buttonEnviar():
            
            if len(mensagem.get("1.0",END))>1 :
        
                textoMensagens =  str(mensagem.get("1.0",END))
                self.enviar(textoMensagens)
                textoMensagens = "\n VOCÊ: \n" + textoMensagens
                self.escrever(textoMensagens)
                mensagem.delete("1.0",END)
        
        frameHistorico = Frame(app)
        frameHistorico.place(x=10,y=10,width=480,height=180)

        self.scrollbar = Scrollbar(frameHistorico, orient='vertical')
        self.scrollbar.place(x=10,y=10,width=480,height=180)

        self.mensagens = Text(frameHistorico,yscrollcommand=self.scrollbar.set)
        self.mensagens.pack()

        self.mensagens['yscrollcommand'] = self.scrollbar.set

        Label(app,text="Informe a mensagem: ", background="#dde", foreground="#000", anchor="s").place(x=10,y=200,width=130,height=20)
        mensagem = Text(app)
        mensagem.place(x=10,y=220,width=425,height=80)

        Button(app,text="Enviar",command=buttonEnviar).place(x=440,y=220,width=50,height=80)
        app.mainloop()
hostA = "localhost"
hostB = "localhost"
portaUsuarioA = 3535
portaUsuarioB = 5353

Usuario(hostA,hostB,portaUsuarioA,portaUsuarioB)








