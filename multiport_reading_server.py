#!/usr/bin/python

import threading
import time
import socketserver
import configparser
import os

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print("%s wrote: " % self.client_address[0])
        print(self.request.getsockname()[1])
        print (self.data)
        self.request.send(self.data.upper())
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":

    cwd = os.getcwd()
    with open(os.getcwd()+"/test_ini.ini" ,'r+') as f:
       sample_config = f.read()
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read_string(sample_config)
    portlist = [] 
    HOST = ''
    ind = 1
    try: 
      for section in config.sections():
        print(config.sections())
        if(section.find('PLATFORM_'+str(ind)) != -1):
          for options in config.options(section):
             if (options.find('lport') != -1 ):
                portlist.append(int(config.get(section,options)))
        ind += 1
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
        time.sleep(0.2)
