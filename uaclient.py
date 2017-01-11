#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
PRACTICA FINAL PTAVI, NEREA PARDO NAVARRO, 11-01-17
'''

import socket
import sys
import os
import hashlib
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
    METHOD = sys.argv[2]
    OPCION = sys.argv[3]
except:
    sys.exit('Usage: python uaclient.py config method opcion')

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

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((IP_RegProxy, int(Puerto_RegProxy)))

if METHOD == 'REGISTER':
    Expires = sys.argv[3]
    Line = 'REGISTER sip:' + Username_A + ':' + Puerto_UAS + ' ' + 'SIP/2.0\r\nExpires: ' + Expires + '\r\n'
    my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
    print('Enviando: ')
    print(Line)
    Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line
    Content_Log(Path_Log, Contenido_Log)
    data = my_socket.recv(1024)
    print('Respuesta Proxy... ', data.decode('utf-8'))
    Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + data.decode('utf-8')
    Content_Log(Path_Log, Contenido_Log)
    Reply_Server = data.decode('utf-8').split('\r\n')
    if Reply_Server[0] == 'SIP/2.0 401 Unauthorized':
        nonce = data.decode('utf-8').split(" ")[5]
        Procc_Autentic = nonce.split("=")[1] + Passwd_A
        Pass_Autentic = hashlib.sha1()
        Pass_Autentic.update(bytes(Procc_Autentic, 'utf-8'))
        Procc_Autentic = Pass_Autentic.digest()
        Line = 'REGISTER sip:' + Username_A + ':' + Puerto_UAS + ' ' + 'SIP/2.0\r\nExpires: ' + Expires + '\r\n' + 'Authorization: Digest response =' + str(Procc_Autentic)
        my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
        Contenido_Log = '\n' + Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line + '\r\n'
        Content_Log(Path_Log, Contenido_Log)
        print('Enviando:')
        print(Line)
        data = my_socket.recv(1024)
        print('Respuesta Proxy... ', data.decode('utf-8'))
        Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + data.decode('utf-8')
        Content_Log(Path_Log, Contenido_Log)

elif METHOD == 'INVITE':
    INVITADO = sys.argv[3]
    v = 'v=0'
    o = 'o=' + Username_A + ' ' + IP_UAS
    s = 's=misesion'
    t = 't=0'
    m = 'm=audio ' + Puerto_RTP + ' ' + 'RTP'
    print(INVITADO)
    Line = 'INVITE sip:' + INVITADO + ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp\r\n' + '\r\n' + v + '\r\n' + o + '\r\n' + s + '\r\n' + t + '\r\n' + m + '\r\n'
    my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
    Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line
    Content_Log(Path_Log, Contenido_Log)
    print('Enviando:')
    print(Line)
    data = my_socket.recv(1024)
    print('Respuesta Proxy... ', data.decode('utf-8'))
    Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + data.decode('utf-8')
    Content_Log(Path_Log, Contenido_Log)
    Reply_Server = data.decode('utf-8').split('\r\n')

    if Reply_Server[0] == ('SIP/2.0 100 Trying SIP/2.0 180 Ring SIP/2.0 200 OK'):
        print('Enviando ACK A PROXY...')
        Line = 'ACK sip:' + INVITADO + ' ' + 'SIP/2.0\r\n'
        my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
        Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line
        Content_Log(Path_Log, Contenido_Log)
        Port_Send = Reply_Server[7].split()[1]
        Dir_SIP = Reply_Server[4].split()[1]
        aEjecutar = './mp32rtp -i ' + '127.0.0.1' + ' -p ' + Port_Send
        aEjecutar += ' < ' + Path_Audio
        print('Vamos a enviar el audio...', aEjecutar)
        os.system(aEjecutar)
        print('Audio enviado')

elif METHOD == 'BYE':
    INVITADO = sys.argv[3]
    Line = 'BYE sip:' + INVITADO + ' ' + 'SIP/2.0\r\n'
    print('Enviando:')
    print(Line)
    my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
    Contenido_Log = Hora_Log + ' Send to ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + Line
    Content_Log(Path_Log, Contenido_Log)
    data = my_socket.recv(1024)
    print('Respuesta Proxy... ', data.decode('utf-8'))
    Contenido_Log = Hora_Log + ' Received from ' + IP_RegProxy + ':' + Puerto_RegProxy + ' ' + data.decode('utf-8')
    Content_Log(Path_Log, Contenido_Log)

print('Cerrando UA...')
my_socket.close()
Contenido_Log = '\n' + Hora_Log + ' Finishing... '
Content_Log(Path_Log, Contenido_Log)
