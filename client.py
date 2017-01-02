#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    OPCION = sys.argv[3]
except:
    sys.exit("Usage: python uaclient.py config method opcion")


class SmallSMILHandler(ContentHandler):
    def __init__(self):
        self.account_username = ""
        self.account_passwd = ""
        self.uaserver_ip = ""
        self.uaserver_puerto = ""
        self.rtpaudio_puerto = ""
        self.regproxy_ip = ""
        self.regproxy_puerto = ""
        self.log_path = ""
        self.audio_path = ""
        self.Datos = []

    def startElement(self, name, attrs):
        if name == 'account':
            self.account_username = attrs.get('username', "")
            self.account_passwd = attrs.get('passwd', "")
            atrib = {'username': self.account_username, 'passwd': self.account_passwd}
            self.Datos.append(atrib)
        elif name == 'uaserver':
            self.uaserver_ip = attrs.get('ip', "")
            self.uaserver_puerto = attrs.get('puerto', "")
            atrib = {'ip' : self.uaserver_ip, 'puerto': self.uaserver_puerto}
            self.Datos.append(atrib)
        elif name == 'rtpaudio':
            self.rtpaudio_puerto = attrs.get('puerto', "")
            atrib = {'puerto': self.rtpaudio_puerto}
            self.Datos.append(atrib)
        elif name == 'regproxy':
            self.regproxy_ip = attrs.get('ip', "")
            self.regproxy_puerto = attrs.get('puerto', "")
            atrib = {'ip': self.regproxy_ip, 'puerto': self.regproxy_puerto}
            self.Datos.append(atrib)
        elif name == 'log':
            self.log_path = attrs.get('path', "")
            atrib = {'path', ""}
            self.Datos.append(atrib)
        elif name == 'audio':
            self.audio_path = attrs.get('path', "")
            atrib = {'path', ""}
            self.Datos.append(atrib)

    def get_tags(self):
        return self.Datos

if __name__ == "__main__":
    parser = make_parser()
    sHandler = SmallSMILHandler()
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

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((str(IP_RegProxy), int(Puerto_RegProxy)))

    if METHOD == 'REGISTER':
        Expire = sys.argv[3]
        Line = "REGISTER sip:" + Username_A + ":" + Puerto_UAS + "SIP/2.0" + Expire + "\r\n"
        my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
        print("Enviando: " + Line)

    elif METHOD == 'INVITE':
        Line1 = "sip:" + Username_A + "SIP/2.0\r\n" + "Content-Type: application/sdp" + "\r\n"
        v = "v=0"
        o = "o=" + Username_A + IP_UAS
        s = "s=misesion"
        t = "t=0"
        m = "m=audio " + Puerto_RTP + "RTP"
        Line = Line1 + '\r\n' + v + '\r\n' + o + '\r\n' + s + '\r\n' + t + '\r\n' + m + '\r\n'
        my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')
        print("Enviando: " + Line)

    elif METHOD == 'BYE':
        Line = "BYE sip:" + Username_A + "SIP/2.0\r\n"
        my_socket.send(bytes(Line, 'utf-8') + b'\r\n\r\n')

    print("Terminando socket...")

    my_socket.close()