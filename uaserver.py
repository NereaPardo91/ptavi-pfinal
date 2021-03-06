"""
PRACTICA FINAL PTAVI, NEREA PARDO NAVARRO, 11-01-17
"""

import socketserver
import socket
import sys
import os
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def Content_Log(Path_Log, Contenido_Log):
    Time_Log = time.time()
    Fichero_Log = open(Path_Log, 'a+')
    Fichero_Log.write(Contenido_Log)
    Fichero_Log.close()


class ReadFich(ContentHandler):
    def __init__(self):
        self.account_username = ''
        self.account_passwd = ''
        self.uaserver_ip = ''
        self.uaserver_puerto = ''
        self.rtpaudio_puerto = ''
        self.regproxy_ip = ''
        self.regproxy_puerto = ''
        self.log_path = ''
        self.audio_path = ''
        self.Datos = []

    def startElement(self, name, attrs):
        if name == 'account':
            self.account_username = attrs.get('username', '')
            self.account_passwd = attrs.get('passwd', '')
            atrib = {'username': self.account_username, 'passwd': self.account_passwd}
            self.Datos.append(atrib)
        elif name == 'uaserver':
            self.uaserver_ip = attrs.get('ip', '')
            self.uaserver_puerto = attrs.get('puerto', '')
            atrib = {'ip': self.uaserver_ip, 'puerto': self.uaserver_puerto}
            self.Datos.append(atrib)
        elif name == 'rtpaudio':
            self.rtpaudio_puerto = attrs.get('puerto', '')
            atrib = {'puerto': self.rtpaudio_puerto}
            self.Datos.append(atrib)
        elif name == 'regproxy':
            self.regproxy_ip = attrs.get('ip', '')
            self.regproxy_puerto = attrs.get('puerto', '')
            atrib = {'ip': self.regproxy_ip, 'puerto': self.regproxy_puerto}
            self.Datos.append(atrib)
        elif name == 'log':
            self.log_path = attrs.get('path', '')
            atrib = {'path': self.log_path}
            self.Datos.append(atrib)
        elif name == 'audio':
            self.audio_path = attrs.get('path', '')
            atrib = {'path': self.audio_path}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos

try:
    CONFIG = sys.argv[1]
except:
    sys.exit("Usage: python server.py config")

parser = make_parser()
sHandler = ReadFich()
parser.setContentHandler(sHandler)
parser.parse(open(CONFIG))
Datos = sHandler.get_tags()

Username_A = Datos[0]['username']
Passwd_A = Datos[0]['passwd']
IP_UAS = Datos[1]['ip']
Puerto_UAS = Datos[1]['puerto']
Puerto_RTP = Datos[2]['puerto']
IP_RegProxy = Datos[3]['ip']
Puerto_RegProxy = Datos[3]['puerto']
Path_Log = Datos[4]['path']
Path_Audio = Datos[5]['path']

Hora_Log = time.time()
Hora_Log = time.strftime('%Y%m%d%H%M%S', time.gmtime(Hora_Log))

Contenido_Log = Hora_Log + ' Starting...\r\n'
Content_Log(Path_Log, Contenido_Log)


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    Port_RTP_Client = {}

    def handle(self):
        Linea = self.rfile.read()
        Linea = Linea.decode('utf-8')
        Line = Linea.split()
        Direccion_SIP = Line[1].split(':')[1]
        Contenido_Log = '\n' + Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Linea
        Content_Log(Path_Log, Contenido_Log)
        print('Recibido de Proxy...\r\n')
        print(Linea)

        if Line[0] == 'INVITE':
            Port_Client = Line[11]
            self.Port_RTP_Client[Direccion_SIP] = [Port_Client]
            print('Enviando a Proxy Confirmacion INVITE...')
            v = 'v=0'
            o = 'o=' + Username_A + ' ' + IP_UAS
            s = 's=misesion'
            t = 't=0'
            m = 'm=audio ' + Puerto_RTP + ' ' + 'RTP'
            Line = ('SIP/2.0 100 Trying SIP/2.0 180 Ring SIP/2.0 200 OK\r\n')
            Line += 'Content-Type: application/sdp\r\n' + '\r\n' + v + '\r\n' + o + '\r\n' + s + '\r\n' + t + '\r\n' + m + '\r\n'
            self.wfile.write(bytes(Line, 'utf-8'))
            Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line
            Content_Log(Path_Log, Contenido_Log)

        elif Line[0] == 'ACK':
            print('Enviando a Proxy Confirmacion ACK...')
            Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + 'ACK'
            Content_Log(Path_Log, Contenido_Log)
            valores = self.Port_RTP_Client[Direccion_SIP]
            aEjecutar = './mp32rtp -i ' + '127.0.0.1' + ' -p ' + str(valores[0])
            aEjecutar += ' < ' + Path_Audio
            print('Vamos a enviar el audio...', aEjecutar)
            os.system(aEjecutar)
            print('Audio enviado')

        elif Line[0] == 'BYE':
            Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Linea
            Content_Log(Path_Log, Contenido_Log)
            print('Enviando a Proxy Confirmacion BYE...')
            self.wfile.write(b'SIP/2.0 200 OK\r\n')
            Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + 'SIP/2.0 200 OK'
            Content_Log(Path_Log, Contenido_Log)

if __name__ == "__main__":
    serv = socketserver.UDPServer((IP_UAS, int(Puerto_UAS)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
    Contenido_Log = '\n' + Hora_Log + ' Finishing...'
    Content_Log(Path_Log, Contenido_Log)
