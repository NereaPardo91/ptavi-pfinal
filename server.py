"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    CONFIG = sys.argv[1]
except:
    sys.exit("Usage: python server.py IP port audio_file")


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
            atrib = {'ip' : self.uaserver_ip, 'puerto': self.uaserver_puerto}
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
            atrib = {'path', ''}
            self.Datos.append(atrib)
        elif name == 'audio':
            self.audio_path = attrs.get('path', '')
            atrib = {'path', ''}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos


parser = make_parser()
sHandler = ReadFich()
parser.setContentHandler(sHandler)
parser.parse(open(CONFIG))
Datos = sHandler.get_tags()
#print(Datos)

Username_A = Datos[0]['username']
Passwd_A = Datos[0]['passwd']
IP_UAS = Datos[1]['ip']
Puerto_UAS = Datos[1]['puerto']
Puerto_RTP = Datos[2]['puerto']
IP_RegProxy = Datos[3]['ip']
Puerto_RegProxy = Datos[3]['puerto']
#Path_Log = Datos[4]['path']
#Path_Audio = Datos[5]['path']


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        Linea = self.rfile.read()
        Linea = Linea.decode('utf-8')
        Line = Linea.split()
        print('Recibido de Proxy...\r\n')
        print(Linea)
        if Line[0] == 'INVITE':
            print('Enviando a Proxy Confirmacion INVITE...')
            self.wfile.write(b'SIP/2.0 100 Trying' + b' ' + b'SIP/2.0 180 Ring' + b' ' + b'SIP/2.0 200 OK')
            #Reply_Proxy = self.rfile.read()
            #Reply_Proxy = Reply_Proxy.decode('utf-8')
            #print('REPLY_PROXY:   ' + Reply_Proxy)
        elif Line[0] == 'ACK':
            #print('REPLY_PROXY:   ' + Linea)
            self.wfile.write(b'RECIBIDO ACK DE PROXY')

if __name__ == "__main__":
    serv = socketserver.UDPServer(('127.0.0.1', int(Puerto_UAS)), EchoHandler)
    print("Lanzando servidor UDP de eco...")
    serv.serve_forever()

