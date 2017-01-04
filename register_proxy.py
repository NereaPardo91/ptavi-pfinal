#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Clase (y programa principal) para un servidor de eco en UDP simple
'''

import socketserver 
import socket
import sys
import time
import json
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    CONFIG = sys.argv[1]
except:
    sys.exit('Usage: python3 proxy_registrar.py config')


class ReadFich(ContentHandler):

    def __init__(self):
        self.server_name = ''
        self.server_ip = ''
        self.server_puerto = ''
        self.database_path = ''
        self.database_passwdpath = ''
        self.log_path = ''
        self.Datos = []

    def startElement(self, name, attrs):
        if name == 'server':
            self.server_name = attrs.get('name', '')
            self.server_ip = attrs.get('ip', '')
            self.server_puerto = attrs.get('puerto', '')
            atrib = {'name': self.server_name, 'ip': self.server_ip, 'puerto': self.server_puerto}
            self.Datos.append(atrib)
        elif name == 'database':
            self.database_path = attrs.get('path', '')
            self.database_passwdpath = attrs.get('passwdpath', '')
            atrib = {'path' : self.database_path, 'passwdpath': self.database_passwdpath}
            self.Datos.append(atrib)
        elif name == 'log':
            self.log_path = attrs.get('path', '')
            atrib = {'path': self.log_path}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos
        
parser = make_parser()
sHandler = ReadFich()
parser.setContentHandler(sHandler)
parser.parse(open(CONFIG))
Datos = sHandler.get_tags()

Name_Proxy = Datos[0]['name']
IP_Proxy = Datos[0]['ip']
Puerto_Proxy = Datos[0]['puerto']
Path_Database = Datos[1]['path']
Passwdpath_Database = Datos[1]['passwdpath']
Log_Path = Datos[2]['path']

my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((('127.0.0.1'), 5555))

class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    '''
    SIPRegister server class
    '''
    list_users = {}

    def handle(self):
        '''
        Registro
        '''
        Linea = self.rfile.read()
        Linea = Linea.decode('utf-8')
        Line = Linea.split()
        print('Mensaje:')
        print(Linea)
        Estado = ''
        if Line[0] == 'REGISTER':
            for i in Line:
                if i == 'Authorization:':
                    Estado = 'Autorizado'
                    self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
            if(Estado != 'Autorizado'):
                self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r\n')
        elif Line[0] == 'INVITE':
            my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
            print('Enviando a Server...')
            print(Linea)
            print('Respuesta Server... ', data.decode('utf-8'))
            data = my_socket.recv(1024)
            Reply_Server = data.decode('utf-8').split('\r\n')
            self.wfile.write(b'paracliente\r\n\r\n')
           


#print(Datos)


if __name__ == '__main__':
    print(Puerto_Proxy)
    serv = socketserver.UDPServer(('', int(Puerto_Proxy)), SIPRegisterHandler)
    print('Listening...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Finalizado servidor')
