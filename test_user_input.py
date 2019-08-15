import re
import threading
from threading import Timer
import time
import socketserver
import configparser
import os
import sys
import urllib
from urllib import parse
from urllib.request import urlopen
from urllib import request
import paramiko
from datetime import datetime
import trace
import socket
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
          self.data = self.request.recv(19200).strip()
          print("%s wrote: " % str(self.client_address))
          self.port = self.request.getsockname()[1]
#          print("%s : " % self.client_address[1])
          print (self.data)
          def hextochr():
             s = ''.join([chr(int(x, 16)) for x in self.data.split()])
             print(s)
          def ordtochr():
             s = ''.join([chr(int(x)) for x in self.data.split()])
             print(s)
          is_hex = re.compile(r'^[+\-]?' '0' '[xX]' '(0|' '([1-9A-Fa-f][0-9A-Fa-f]*))$').match
          for x in self.data.decode("ascii").split():
             if bool(is_hex(x)):
                hextochr()
                break
             else:
                ordtochr()
                break
#          print([chr(int(x, 16))])

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    portlist = []
    p_no =[]
    HOST = ''
    cwd = os.getcwd()

    with open(cwd+"/server.ini" ,'r+') as f:
      sample_config = f.read()
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read_string(sample_config)
    try:
      ind = 1
      for section in config.sections():
        if('PLATFORM_'+str(ind) == section ):
           for options in config.options(section):
              if ('lport' == options ):
                lport = config.get(section,options).strip("\"")
                portlist.append(int(lport))
                p_no.append(ind)
                ind += 1
      print(portlist)
    except:
      print("config file not found")

    def create_thread(HOST,PORT):
         server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
         server_thread = threading.Thread(target=server.serve_forever)
         server_thread.setDaemon(True)
         server_thread.start()

    for port in portlist:
       create_thread(HOST,port)

    while 1:
        time.sleep(0.1)


