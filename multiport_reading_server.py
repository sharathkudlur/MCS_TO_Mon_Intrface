#!/usr/bin/python

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
cmd_tic = ''

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
      try:
        global cmd_tic
        today = datetime.now()
        while True:
          def ERROR(address,port):
            global cmd_tic
            if (cmd_tic[:1] == 'L'):
               cmd_tic = ''
               print("Error")
               print(threading.enumerate())
               timer.cancel()
#               s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
               self.request.send(bytes("E","ascii"))
               print(threading.currentThread().getName())
               print(threading.enumerate())
#               python=sys.executable
#              os.execl(python, python, * sys.argv)
            else:
               cmd_tic = ''
          self.data = self.request.recv(19200).strip()
          print("%s wrote: " % str(self.client_address))
          self.port = self.request.getsockname()[1]
#          print("%s : " % self.client_address[1])
          print (self.data)
          s = ''.join([chr(int(x, 16)) for x in self.data.split()])
          s = s.strip()
          print(s)
          timer = Timer(10,ERROR,args=(self.client_address[0],self.client_address[1],))
#          timer.setDaemon(True)
          while timer.is_alive():
             timer.cancel()
          print(len(s),len(cmd_tic),cmd_tic,cmd_tic[:1])
          if (len(s) <= 4 and (len(cmd_tic) <= 4) and (s != 'S') and (cmd_tic == '' or cmd_tic[:1] == 'L')):
              cmd_tic += s
              e_port = str(self.port)
              print(e_port)

              if len(cmd_tic) < 4 and cmd_tic[:1] == 'L':
                    print("False, timer start")
                    timer.start()

              s = ''.join(cmd_tic)
              if cmd_tic[:1] != 'L':
                 cmd_tic = ''
              print(s)
          if len(cmd_tic) >= 4 :
             cmd_tic = ''
             timer.cancel()

          if (len(s) == 4 and (s.find('L') != -1) and int(s[1:4]) > 0):
                count_down = {"time": s[1:], "count": "down", "status": "start"}
                q_count_down = parse.urlencode(count_down)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                print(TOM_IP)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_down
                html = send_url_cmd(url)
                logs = html + " " + str(today) + " Time Interval Clock Down Start"
                log_file(logs)
                update_log_to_SMMS(logs)
                self.request.send(bytes("K", "ascii"))

          if ((s.find('L000') != -1) and len(s) == 4):
                count_up = {"time": s[1:], "count": "up", "status": "start"}
                q_count_up = parse.urlencode(count_up)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                print(TOM_IP)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_up
                html = send_url_cmd(url)
                logs = html + " " + str(today) + " Time Interval Clock Up Start"
                log_file(logs)
                update_log_to_SMMS(logs)
                self.request.send(bytes("K", "ascii"))

          if ((s.find('S') != -1) and s == 'S'):
                count_stop = {"status": "stop"}
                q_count_stop = parse.urlencode(count_stop)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                print(TOM_IP)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_stop
                send_url_cmd(url)
                html = send_url_cmd(url)
                logs = html + " " + str(today) + " Time Interval Clock Stop"
                log_file(logs)
                update_log_to_SMMS(logs)

          if (s.find('THD-O') != -1):
                if (s.find('THD-ON') != -1):
                   result_html = TRAIN_HOLD_ON(s)
                   logs = result_html + " " + str(today) + " Train Hold ON"
                   log_file(logs)
                   update_log_to_SMMS(logs)
                   self.request.send(bytes("THD-ACK", "ascii"))
                elif (s.find('THD-OFF') != -1):
                   result_html = TRAIN_HOLD_OFF(s)
                   logs = result_html + " " + str(today) + " Train Hold OFF"
                   log_file(logs)
                   update_log_to_SMMS(logs)
                   self.request.send(bytes("THD-NAK", "ascii"))


          if (len(s) >= 6 and (s.find('KP') != -1)):
                monid = s[2:4].lstrip("0")
                camid = s[4:7].lstrip("0")
                THD_DIR = config.get("CONF","DIR").strip('\"')
                FTHD_INF = config.get("CONF","FILE_THD_INFO").strip('\"')
                try:
                    pfcsv = open(THD_DIR+"/"+FTHD_INF,'r')
                    for line in pfcsv:
                        templist = []
                        for a in line.split(","):
                            templist.append(a.rstrip("\n"))
                        if monid in templist[3] and (camid in templist[1] or camid in templist[2]):
                           ip = config.get("PLATFORM_"+templist[0] ,"TO_MONITOR_IP_ADDR").strip('\"')
                           if (templist[1] == camid):  #int(cam_i) == 1:
                              result_html = TRAIN_HOLD_ON(ip)
                              logs = result_html + " " + str(today) + " Train Hold ON, selection Cam-ID :"+ camid +" and Mon-ID :"+monid
                              log_file(logs)
                              update_log_to_SMMS(logs)
                           elif (templist[2] == camid):  #int(cam_i) == 2:
                              result_html = TRAIN_HOLD_OFF(ip)
                              logs = result_html + " " + str(today) + " Train Hold OFF, selection Cam-ID :"+ camid +" and Mon-ID :"+monid
                              log_file(logs)
                              update_log_to_SMMS(logs)
                finally:
                    pfcsv.close()
      except urllib.error.URLError:
        print("IP not Found")
      finally:
        self.request.close()

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

    COMP = config.get("SMMS_INFO","HOST_IP").strip('\"')
    USER = config.get("SMMS_INFO","USER_NAME").strip('\"')
    PSW = config.get("SMMS_INFO","PASSWORD").strip('\"')
    LOGP = config.get("SMMS_INFO","LOG_FILE_PATH").strip('\"')

    def update_log_to_SMMS(log_str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
                ssh.connect(COMP, username=USER, password=PSW, allow_agent = False)
        except paramiko.SSHException:
                print("Connectin Failed to SMMS server")
                quit()
        print(log_str)
#       print(LOGP)
        stdin,stdout,stderr = ssh.exec_command("cd " + LOGP +" && d: && echo \"" +  log_str  +"\" >> server_cmd_prg.txt")
        for line in stdout.readlines():
                print(line.strip())
        ssh.close()

    def log_file(logs):
        f = open(cwd+"/server_cmd_prg.log", "a+")
        f.write(logs + "\n")

    def send_url_cmd(string):
        result = urllib.request.urlopen(string)
        html = result.read().decode("UTF-8")
        print(html)
        return html

    def PLATFORM_TOM_IP(p):
        i = 1
        if p in portlist:
           print(p)
           for section in config.sections(): 
               if('PLATFORM_'+str(i) == section ):
                  for options in config.options(section):
                     val = config.get(section,options).strip("\"")
                     if options == 'lport':
                        if ( int(p) == int(val) ):
                           return ip
                     if(options == 'to_monitor_ip_addr'):
                        ip = config.get(section,options).strip("\"")
                        i += 1
        elif(p.find('THD-O') != -1):
           for spl in p.split():
               for j in p_no:
                   if spl in str(j):
                      ip = config.get("PLATFORM_"+spl ,"TO_MONITOR_IP_ADDR").strip('\"') 
                      return ip
        elif (p.find('.') != -1):
           print(p)
           return p

    def TRAIN_HOLD_ON(arg):
        THD_ON = {"status": "start"}
        Q_THD_ON = parse.urlencode(THD_ON)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        print(L_TOM_IP)
        url = "http://" + L_TOM_IP + "/trainhold.cgi?" + Q_THD_ON
        send_url_cmd(url)
        html = send_url_cmd(url)
        return html

    def TRAIN_HOLD_OFF(arg):
        THD_OFF = {"status": "stop"}
        Q_THD_OFF = parse.urlencode(THD_OFF)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        print(L_TOM_IP)
        url = "http://" + L_TOM_IP + "/trainhold.cgi?" + Q_THD_OFF
        send_url_cmd(url)
        html = send_url_cmd(url)
        return html

    def create_thread(HOST,PORT):
       server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
       server_thread = threading.Thread(target=server.serve_forever)
       server_thread.setDaemon(True)
       server_thread.start()
     
    for port in portlist:
       create_thread(HOST,port)

    while 1:
        time.sleep(0.1)
