#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
PRACTICA FINAL PTAVI, NEREA PARDO NAVARRO, 11-01-17
'''

import socketserver
import socket
import sys
import time
import json
import hashlib
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


def Content_Log(Path_Log, Contenido_Log):
    Time_Log = time.time()
    Fichero_Log = open(Path_Log, 'a+')
    Fichero_Log.write(Contenido_Log)
    Fichero_Log.close()


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
            atrib = {'path': self.database_path, 'passwdpath': self.database_passwdpath}
            self.Datos.append(atrib)
        elif name == 'log':
            self.log_path = attrs.get('path', '')
            atrib = {'path': self.log_path}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos

try:
    CONFIG = sys.argv[1]
except:
    sys.exit('Usage: python3 proxy_registrar.py config')

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
Path_Log = Datos[2]['path']

Hora_Log = time.time()
Hora_Log = time.strftime('%Y%m%d%H%M%S', time.gmtime(Hora_Log))

Contenido_Log = Hora_Log + ' Starting...\r\n'
Content_Log(Path_Log, Contenido_Log)


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
        Puerto_Cliente = self.client_address[1]
        IP = str(Direccion_IP)
        Direccion_SIP = Line[1].split(':')
        SIP_Fich_Password = Direccion_SIP[1]
        Direccion_SIP = Direccion_SIP[0] + ':' + Direccion_SIP[1]
        Contenido_Log = '\n' + Hora_Log + ' Received from ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + Linea + '\r\n'
        Content_Log(Path_Log, Contenido_Log)
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
                        if SIP_Fich_Password == j.split(',')[0]:
                            Password_Fich = j.split(',')[1]
                            Password_Fich = Password_Fich.split('\n')[0]
                            Procc_Autentic = nonce + Password_Fich
                            Pass_Autentic = hashlib.sha1()
                            Pass_Autentic.update(bytes(Procc_Autentic, 'utf-8'))
                            Procc_Autentic = Pass_Autentic.digest()
                            Procc_Autentic_Client = Line[8].split('=')[1]
                    if str(Procc_Autentic) == Procc_Autentic_Client:
                        Autentificacion = 1
                        print("Contraseñas iguales\n")
                    else:
                        print("Contraseña incorrecta\n")
                        self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r')
                        Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + 'SIP/2.0 401 Unauthorized' + '\r\n'
                        Content_Log(Path_Log, Contenido_Log)

                    if Autentificacion == 1:
                        Puerto_Client = Line[1].split(':')[2]
                        Expires = Line[4]
                        Hora_Act = time.time()
                        Hora_Expiracion = Hora_Act + int(Expires)
                        Hora = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(Hora_Expiracion))
                        Estado = 'Autorizado'
                        self.wfile.write(b'SIP/2.0 200 OK\r\n\r\n')
                        Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + 'SIP/2.0 200 OK' + '\r\n'
                        Content_Log(Path_Log, Contenido_Log)
                        self.list_users[Direccion_SIP] = [IP, Hora, Puerto_Client, Expires]
                        fichjson = self.register2json()
                        if Expires == 0:
                            del self.list_users[Direccion_SIP]

            if(Estado != 'Autorizado'):
                self.wfile.write(b'SIP/2.0 401 Unauthorized\r\n\r\nWWW Authenticate: Digest nonce=' + bytes(nonce, 'utf-8'))
                Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + 'SIP/2.0 401 Unauthorized WWW Authenticate: Digest nonce=' + nonce
                Content_Log(Path_Log, Contenido_Log)

        elif Line[0] == 'INVITE':
            for i in self.list_users.keys():
                if Direccion_SIP == i:
                    valores = self.list_users[Direccion_SIP]
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((('127.0.0.1'), int(valores[2])))
                    my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
                    Contenido_Log = Hora_Log + ' Send to ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + Linea + '\r\n'
                    Content_Log(Path_Log, Contenido_Log)
                    print('Enviando a Server...')
                    print(Linea)
                    data = my_socket.recv(1024)
                    print('Respuesta Server... ', data.decode('utf-8'))
                    Contenido_Log = Hora_Log + ' Received ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + Linea
                    Content_Log(Path_Log, Contenido_Log)
                    self.wfile.write(data)
                    Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + data.decode('utf-8')
                    Content_Log(Path_Log, Contenido_Log)
                    REGISTRADO = 1
            if REGISTRADO == 0:
                self.wfile.write(b'SIP/2.0 404 User Not Found')
                Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + 'SIP/2.0 404 User Not Found'
                Content_Log(Path_Log, Contenido_Log)

        elif Line[0] == 'ACK':
            valores = self.list_users[Direccion_SIP]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((('127.0.0.1'), int(valores[2])))
            my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')

            Contenido_Log = Hora_Log + ' Send to ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + Linea + '\r\n'
            Content_Log(Path_Log, Contenido_Log)

            print('Enviando a Server...')
            print(Linea)
            data = my_socket.recv(1024)
            print('Respuesta Server... ', data.decode('utf-8'))
            Contenido_Log = Hora_Log + ' Received ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + data.decode('utf-8')
            Content_Log(Path_Log, Contenido_Log)
            self.wfile.write(data)
            Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + data.decode('utf-8')
            Content_Log(Path_Log, Contenido_Log)

        elif Line[0] == 'BYE':
            valores = self.list_users[Direccion_SIP]
            my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((('127.0.0.1'), int(valores[2])))
            my_socket.send(bytes(Linea, 'utf-8') + b'\r\n\r\n')
            Contenido_Log = Hora_Log + ' Send to ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + Linea + '\r\n'
            Content_Log(Path_Log, Contenido_Log)
            print('Enviando a Server...')
            print(Linea)
            data = my_socket.recv(1024)
            Contenido_Log = Hora_Log + ' Received ' + str(valores[0]) + ':' + str(valores[2]) + ' ' + data.decode('utf-8')
            Content_Log(Path_Log, Contenido_Log)
            print('Respuesta Server... ', data.decode('utf-8'))
            self.wfile.write(data)
            Contenido_Log = Hora_Log + ' Send to ' + str(Direccion_IP) + ':' + str(Puerto_Cliente) + ' ' + data.decode('utf-8')
            Content_Log(Path_Log, Contenido_Log)

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
    print('Server ' + Name_Proxy + ' listening at port ' + Puerto_Proxy + '...')
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print('Finalizado servidor')
        Contenido_Log = Hora_Log + ' Finishing...'
        Content_Log(Path_Log, Contenido_Log)
