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
import hashlib

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
        print('Recibido de Cliente:')
        print(Linea)
        Direccion_IP = self.client_address[0]
        IP = str(Direccion_IP) 
        Direccion_SIP = Line[1].split(':')
        dir_SIP = Direccion_SIP[1]
        Direccion_SIP = Direccion_SIP[0] + ':' + Direccion_SIP[1]
        Estado = ''
        REGISTRADO = 0
        nonce = '1234123412341234'
        Passwords_List = []
        Autentificacion = 0

        with open('passwords', 'r') as Contraseñas:
            for i in Contraseñas:
                Passwords_List.append(i)

        if Line[0] == 'REGISTER':
            for i in Line:
                if i == 'Authorization:':
                    for j in Passwords_List:
                        if dir_SIP == j.split(",")[0]:
                            contraseñaFich = j.split(",")[1]
                            contraseñaFich = contraseñaFich.split("\n")[0]
                            Procc_Autentic = nonce + contraseñaFich
                            Pass_Autentic = hashlib.sha1()
                            Pass_Autentic.update(bytes(Procc_Autentic,'utf-8'))
                            Procc_Autentic = Pass_Autentic.digest()
                            Procc_Autentic_Client = Line[8].split("=")[1]
                    if str(Procc_Autentic) == Procc_Autentic_Client:
                        Autentificacion = 1
                        print("Contraseñas iguales\n")
                    else:
                        print("Contraseña incorrecta\n")
                        self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r\n')
                    if Autentificacion == 1:
                        Puerto_Client = Line[1].split(':')[2]
                        Expires = Line[4]
                        Hora_Act = time.time()
                        Hora_Expiracion = Hora_Act + int(Expires)
                        Hora = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(Hora_Expiracion))
                        Estado = 'Autorizado'
                        self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
                        self.list_users[Direccion_SIP] = [IP, Hora, Puerto_Client, Expires]
                        fichjson = self.register2json()

            if(Estado != 'Autorizado'):
                self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r\nWWW Authenticate: Digest nonce=' + bytes(nonce, 'utf-8'))

        elif Line[0] == 'INVITE':
            for i in self.list_users.keys():
                if Direccion_SIP == i:
                    valores = self.list_users[Direccion_SIP]
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((('127.0.0.1'), int(valores[2])))
                    my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
                    print('Enviando a Server...')
                    print(Linea)
                    data = my_socket.recv(1024)
                    print('Respuesta Server... ', data.decode('utf-8'))
                    self.wfile.write(data)
                    REGISTRADO = 1
            if REGISTRADO == 0:
                self.wfile.write(b'SIP/2.0 404 User Not Found')

        elif Line[0] == 'ACK':
            valores = self.list_users[Direccion_SIP]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((('127.0.0.1'), int(valores[2])))
            my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
            print('Enviando a Server...')
            print(Linea)
            data = my_socket.recv(1024)
            print('Respuesta Server... ', data.decode('utf-8'))
            self.wfile.write(data)

        elif Line[0] == 'BYE':
            valores = self.list_users[Direccion_SIP]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((('127.0.0.1'), int(valores[2])))
            my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
            print('Enviando a Server...')
            print(Linea)
            data = my_socket.recv(1024)
            print('Respuesta Server... ', data.decode('utf-8'))
            self.wfile.write(data)


    def register2json(self):
        """
        Creacion fichero json
        """
        json.dump(self.list_users, open('Registro_Usuarios.json', 'w'))

    def registered(self):
        """
        Comprobacion existencia fichero json
        """
        try:
            with open("Registro_Usuarios.json") as jsonFile:
                self.list_users = json.load(jsonFile)
        except:
            pass


if __name__ == '__main__':
    serv = socketserver.UDPServer(('', int(Puerto_Proxy)), SIPRegisterHandler)
    print('Listening...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Finalizado servidor')
