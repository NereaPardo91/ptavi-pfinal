#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver 
import sys
import time
import json
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    CONFIG = sys.argv[1]
except:
    sys.exit("Usage: python3 proxy_registrar.py config")


class ReadFich(ContentHandler):

    def __init__(self):
        self.server_name = ""
        self.server_ip = ""
        self.server_puerto = ""
        self.database_path = ""
        self.database_passwdpath = ""
        self.log_path = ""
        self.Datos = []

    def startElement(self, name, attrs):
        if name == 'server':
            self.server_name = attrs.get('name', "")
            self.server_ip = attrs.get('ip', "")
            self.server_puerto = attrs.get('puerto', "")
            atrib = {'name': self.server_name, 'ip': self.server_ip, 'puerto': self.server_puerto}
            self.Datos.append(atrib)
        elif name == 'database':
            self.database_path = attrs.get('path', "")
            self.database_passwdpath = attrs.get('passwdpath', "")
            atrib = {'path' : self.database_path, 'passwdpath': self.database_passwdpath}
            self.Datos.append(atrib)
        elif name == 'log':
            self.log_path = attrs.get('path', "")
            atrib = {'path': self.log_path}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos

class SIPRegisterHandler(socketserver.DatagramRequestHandler):

    """
    SIPRegister server class
    """
    list_users = {}

    def handle(self):

        """
        Registro
        """
        Linea = self.rfile.read()
        Line = Linea.decode('utf-8').split()
        print(Linea.decode('utf-8'))
        todoOk =""
        if Line[0] == 'REGISTER':
            for i in Line:
                if i == "Authorization:":
                    todoOk = "todo ok"
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    print(todoOk)
            if(todoOk != "todo ok"):
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\n\r\n")

parser = make_parser()
sHandler = ReadFich()
parser.setContentHandler(sHandler)
parser.parse(open(CONFIG))
Datos = sHandler.get_tags()
#print(Datos)

Name_Server = Datos[0]['name']
IP_Server = Datos[0]['ip']
Puerto_Server = Datos[0]['puerto']
Path_Database = Datos[1]['path']
Passwdpath_Database = Datos[1]['passwdpath']
Log_Path = Datos[2]['path']

    #my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #my_socket.connect((str(IP_RegProxy), int(Puerto_RegProxy)))

if __name__ == "__main__":
    serv = socketserver.UDPServer(('', 7777), SIPRegisterHandler)
    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")