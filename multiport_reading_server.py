#!/usr/bin/python

import threading
import time
import socketserver
import configparser
import os
import urllib
from urllib import parse
from urllib.request import urlopen
from urllib import request
import paramiko
from datetime import datetime

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        today = datetime.now()

        self.data = self.request.recv(19200).strip()
        print("%s wrote: " % self.client_address[0])
        self.port = self.request.getsockname()[1]
        print (self.data)
        self.request.send(bytes("K", "ascii"))
        self.request.send(self.data.upper())
        s = ''.join([chr(int(x, 16)) for x in self.data.split()])
        s = s.strip()
        print(s)
        if len(s) == 4 and s != 'L000':
                count_down = {"time": s[1:], "count": "down", "status": "start"}
                q_count_down = parse.urlencode(count_down)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                print(TOM_IP)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_down
                html = send_url_cmd(url)
                print(html + " " + str(today) + " Time Interval Clock Down Start")
                logs = html + " " + str(today) + " Time Interval Clock Down Start"
                log_file(logs)
                update_log_to_SMMS(logs)

        if (s.find('L000') != -1):
                count_up = {"time": s[1:], "count": "up", "status": "start"}
                q_count_up = parse.urlencode(count_up)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_up
                html = send_url_cmd(url)
                print(html + " " + str(today) + " Time Interval Clock Up Start")
                logs = html + " " + str(today) + " Time Interval Clock Up Start"
                log_file(logs)
                update_log_to_SMMS(logs)

        if (s.find('S') != -1):
                count_stop = {"status": "stop"}
                q_count_stop = parse.urlencode(count_stop)
                TOM_IP = PLATFORM_TOM_IP(self.port)
                url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_stop
                send_url_cmd(url)
                html = send_url_cmd(url)
                print(html + " " + str(today) + " Time Interval Clock Stop")
                logs = html + " " + str(today) + " Time Interval Clock Stop"
                log_file(logs)
                update_log_to_SMMS(logs)

        if (s.find('THD-ON') != -1):
                
                result_html = TRAIN_HOLD_ON(s)
                print(result_html + " " + str(today) + " Train Hold ON")
                logs = result_html + " " + str(today) + " Train Hold ON"
                log_file(logs)
                update_log_to_SMMS(logs)

        if (s.find('THD-OFF') != -1):
                THD_OFF = {"status": "stop"}
                Q_THD_OFF = parse.urlencode(THD_OFF)
                TOM_IP = PLATFORM_TOM_IP(s)
                url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_OFF
                send_url_cmd(url)
                html = send_url_cmd(url)
                print(html + " " + str(today) + " Train Hold OFF")
                logs = html + " " + str(today) + " Train Hold OFF"
                log_file(logs)
                update_log_to_SMMS(logs)

        if (len(s) >= 6 and (s.find('KP') != -1)):
                monid = p[2:4]
                camid = p[4:7]
                print(camid)
                try:
                    pfcsv = open('/home/c4988/share/HOK.txt','r')
                    for line in pfcsv:
                        templist = []
                        for a in line.split(","):
                            templist.append(a.rstrip("\n"))
                            if monid in list and camid in list:
                               ip = config.get("PLATFORM_"+list[0] ,"TO_MONITOR_IP_ADDR").strip('\"')
                               cam_i = templist.index(camid)
                finally:
                    fcsv.close()
                if int(cam_i) == 1:
                   result_html = TRAIN_HOLD_ON(ip)
                   print(result_html + " " + str(today) + " Train Hold ON, selection Cam-ID :"+ camid +"and Mon-ID :"+monid)
                   logs = result_html + " " + str(today) + " Train Hold ON, selection Cam-ID :"+ camid +"and Mon-ID :"+monid
                   log_file(logs)
                   update_log_to_SMMS(logs)
                elif int(cam_i) == 2:
                   result_html = TRAIN_HOLD_OFF(ip)
                   print(result_html + " " + str(today) + " Train Hold OFF, selection Cam-ID :"+ camid +"and Mon-ID :"+monid)
                   logs = result_html + " " + str(today) + " Train Hold OFF, selection Cam-ID :"+ camid +"and Mon-ID :"+monid
                   log_file(logs)
                   update_log_to_SMMS(logs)

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
                print("Connectin Failed")
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

    def TRAIN_HOLD_ON(arg):
        THD_ON = {"status": "start"}
        Q_THD_ON = parse.urlencode(THD_ON)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_ON
        send_url_cmd(url)
        html = send_url_cmd(url)
        return html

    def TRAIN_HOLD_OFF(arg):
        THD_ON = {"status": "stop"}
        Q_THD_ON = parse.urlencode(THD_ON)
        L_TOM_IP = PLATFORM_TOM_IP(arg)
        print(list(L_TOM_IP))
        url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_ON
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
        time.sleep(0.2)
