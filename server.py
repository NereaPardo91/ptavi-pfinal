"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os

try:
    IP = sys.argv[1]
    P = int(sys.argv[2])
    Audio = sys.argv[3]
except:
    sys.exit("Usage: python server.py IP port audio_file")


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        line = self.rfile.read()
        print("El cliente nos manda " + line.decode('utf-8'))
        line = line.decode('utf-8').split()

        if line[0] == 'INVITE':
            self.wfile.write(b'SIP/2.0 100 Trying' + b' ' + b'SIP/2.0 180 Ring' + b' ' + b'SIP/2.0 200 OK')
        elif line[0] == 'BYE':
            self.wfile.write(b'SIP/2.0 200 OK')
        elif line[0] == 'ACK':
            aEjecutar = './mp32rtp -i 127.0.0.1 -p 23032 <' + Audio
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)
            print("Audio enviado")
        elif len(lista) != 2:
            self.wfile.write(b'SIP/2.0 400 Bad Request')
        else:
            self.wfile.write(b'SIP/2.0 405 Method Not Allowed')

if __name__ == "__main__":
    serv = socketserver.UDPServer(('', P), EchoHandler)
    print("Lanzando servidor UDP de eco...")
serv.serve_forever()