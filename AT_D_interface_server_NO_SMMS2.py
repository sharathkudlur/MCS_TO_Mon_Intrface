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
import logging
import re
cmd_tic = ''

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
      try:
        global cmd_tic
        today = datetime.now()
        while True:
          def ERROR(request):
             global cmd_tic
             if (cmd_tic[:1] == 'L'):
                cmd_tic = ''
                print("Error")
                timer.cancel()
                request.send(bytes("E","ascii"))
             else:
                cmd_tic = ''
          self.data = self.request.recv(19200).strip()
          print("%s wrote: " % str(self.client_address))
          self.port = self.request.getsockname()[1]
#          print("%s : " % self.client_address[1])
          print (self.data)
          is_hex = re.compile(r'^[+\-]?' '0' '[xX]' '(0|' '([1-9A-Fa-f][0-9A-Fa-f]*))$').match
          for x in self.data.decode("ascii").split():
             if bool(is_hex(x)):
                s = ''.join([chr(int(x, 16)) for x in self.data.split()])
                break
             else:
                s = ''.join([chr(int(x)) for x in self.data.split()])
                break

          s = s.strip()
          print(s)
          timer = Timer(10,ERROR,args=(self.request,))
#          while timer.is_alive():
#             timer.cancel()
          if (len(s) <= 4 and (len(cmd_tic) <= 4) and (s != 'S') and (cmd_tic == '' or cmd_tic[:1] == 'L')):
              while timer.is_alive():
                 timer.cancel()
              cmd_tic += s
              if len(cmd_tic) < 4 and cmd_tic[:1] == 'L':
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
                logs = html + " " +  TOM_IP + " " + str(today) + " Time Interval Clock Down Start"
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
                logs = html + " " + TOM_IP + " " +str(today) + " Time Interval Clock Up Start"
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
                logs = html + " " + TOM_IP + " " +str(today) + " Time Interval Clock Stop"
                log_file(logs)
                update_log_to_SMMS(logs)
                self.request.send(bytes("K", "ascii"))

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
                   self.request.send(bytes("THD-ACK", "ascii"))

          def cmd_camera_selection(monid,camid):
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
#                        if monid in templist[3] and (camid in templist[1] or camid in templist[2]):
#                           self.request.sendall(self.data.upper())
                finally:
                    pfcsv.close()

          if (len(s) >= 6 and (s.find('CA') != -1)):
             cmd_ca =s.index('CA')
             monid = s[cmd_ca+3:cmd_ca+6].lstrip("0")
             camid = s[cmd_ca+10:cmd_ca+13].lstrip("0")
             print(monid,camid)
             cmd_camera_selection(monid,camid)
          if (len(s) >= 6 and (s.find('KP') != -1)):
                monid = s[2:4].lstrip("0").lstrip("0")
                camid = s[4:7].lstrip("0").lstrip("0")
                cmd_camera_selection(monid,camid)

      except urllib.error.URLError:
        print("Error: TO Monitor IP not Found")
        log_file( self.data.decode("ascii") + " :Error: TO Monitor IP not Found")
      except ConnectionResetError:
        print("Error: Connection reset by the peer!")
        log_file( "Connection reset by the peer!")
      except UnicodeDecodeError as e:
        log_file("Error:%s"% str(e))
      except Exception as ex:
        log_file(self.data.decode("ascii") + "Error: %s"% str(ex))
      finally:
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
  try:
    portlist = []
    p_no =[]
    HOST = ''
    cwd = os.getcwd()

    def log_file(logs):
        f = open(cwd+"/server_cmd_prg.log", "a+")
        f.write(logs)
        f.write("\n")

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
      log_file(logs + " :Error: config file not found")

#    COMP = config.get("SMMS_INFO","HOST_IP").strip('\"')
#    USER = config.get("SMMS_INFO","USER_NAME").strip('\"')
#    PSW = config.get("SMMS_INFO","PASSWORD").strip('\"')
#    LOGP = config.get("SMMS_INFO","LOG_FILE_PATH").strip('\"')

    def update_log_to_SMMS(log_str):
#        ssh = paramiko.SSHClient()
#        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#        try:
#                ssh.connect(COMP, username=USER, password=PSW, allow_agent = False)
#        except paramiko.SSHException:
#                print("Failed to Connect SMMS server!")
#                logs = "Failed to Connect SMMS server!"
#                log_file(logs)
#                quit()
        print(log_str)
#        stdin,stdout,stderr = ssh.exec_command("cd " + LOGP +" && d: && echo \"" +  log_str  +"\" >> server_cmd_prg.txt")
#        for line in stdout.readlines():
#                print(line.strip())
#        ssh.close()


    def send_url_cmd(string):
      try:
        result = urllib.request.urlopen(string)
        return result.read().decode("UTF-8")
      except Exception as e:
        log_file(string + " :Error: %s"% str(e))

    def PLATFORM_TOM_IP(p):
      try:
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
#           print(p)
           return p
      except Exception as e:
        log_file(p + " :Error: %s"% str(e))

    def TRAIN_HOLD_ON(arg):
      try:
        THD_ON = {"status": "start"}
        Q_THD_ON = parse.urlencode(THD_ON)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        print(L_TOM_IP)
        url = "http://" + L_TOM_IP + "/trainhold.cgi?" + Q_THD_ON
        html = send_url_cmd(url)
        return html + " " + L_TOM_IP
      except TypeError:
          print("Platform Number or TO Monitor IP not found in 'file' Train Hold information")
          log_file(arg + " :Error: Platform Number or  TO Monitor IP not found in 'file' Train Hold information")
          exit()

    def TRAIN_HOLD_OFF(arg):
      try:
        THD_OFF = {"status": "stop"}
        Q_THD_OFF = parse.urlencode(THD_OFF)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        print(L_TOM_IP)
        url = "http://" + L_TOM_IP + "/trainhold.cgi?" + Q_THD_OFF
        html = send_url_cmd(url)
        return html + " " + L_TOM_IP
      except TypeError:
          print("Platform Number or TO Monitor IP not found in 'file' Train Hold information")
          log_file(arg + " :Error: Platform Number or TO Monitor IP not found in 'file' Train Hold information")
          exit()

    def create_thread(HOST,PORT):
      try:
         server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
         server_thread = threading.Thread(target=server.serve_forever)
         server_thread.setDaemon(True)
         server_thread.start()
      except Exception as e:
         log_file(str(HOST)+str(PORT)+" :Error: %s"% str(e))

    for port in portlist:
       create_thread(HOST,port)

    while 1:
        time.sleep(0.1)
  except Exception as ex:
    log_file("Error: %s"% str(ex))
