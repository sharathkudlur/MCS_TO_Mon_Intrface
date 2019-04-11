#!/usr/bin/python3.7
import serial
import time
import io
import sys
import urllib
from urllib import parse
from urllib.request import urlopen
from urllib import request
import paramiko
import socket

from datetime import datetime

import codecs
import binascii
import subprocess
import configparser

config = configparser.ConfigParser()
config.read('/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf')

lp = config.get("CONF","LPORT").strip('\"')
COMP = config.get("SMMS_INFO","HOST_IP")
USER = config.get("SMMS_INFO","USER_NAME")
PSW = config.get("SMMS_INFO","PASSWORD")
LOGF = config.get("SMMS_INFO","LOG_FILE_PATH").strip('\"')

TOM_IP_1 = config.get("PLATFORM_1","TO_MONITOR_IP_ADDR").strip('\"')
TOM_IP_2 = config.get("PLATFORM_2","TO_MONITOR_IP_ADDR").strip('\"')
TOM_IP_3 = config.get("PLATFORM_3","TO_MONITOR_IP_ADDR").strip('\"')
TOM_IP_4 = config.get("PLATFORM_4","TO_MONITOR_IP_ADDR").strip('\"')

subprocess.Popen(["socat", "pty,link=/dev/ttyS1", "tcp-listen:" +lp])

time.sleep(5) 
port = '/dev/ttyS1' 
baud = 9600

ser = serial.Serial(port, baud, timeout=1)
ser.reset_input_buffer()
today = datetime.now()
year = time.asctime(time.localtime(time.time()))
ser.write(year.encode())
ser.write(b'Give a Input Value:\r\n')

HOK = { "platform": (1,2,3,4), "cam_id_thd": (111,108,110,109), "cam_id_no_thd": (1,1,29,30), "mon_id": (52,53,54,55) } 
KOW = { "platform": (1,2,3,4), "cam_id_thd": (142,143,144,145), "cam_id_no_thd": (1,2,6,7), "mon_id": (52,53,54,55) }
OLY = { "platform": (1,2), "cam_id_thd": (27,28), "cam_id_no_thd": (1,2), "mon_id": (40,41) }
LAK = { "platform": (3,4), "cam_id_thd": (39,38), "cam_id_no_thd": (1,2), "mon_id": (61,62) }
TSY = { "platform": (1,2,3,4), "cam_id_thd": (77,79,78,80), "cam_id_no_thd": (43,2,42,1), "mon_id": (52,53,54,55) }
SUN = { "platform": (1,2), "cam_id_thd": ("044","045"), "cam_id_no_thd": ('001','002'), "mon_id": ('008','009') }
TUC = { "platform": (1,2), "cam_id_thd": (21,22), "cam_id_no_thd": (1,2), "mon_id": (40,41) }
AIR = { "platform": (1,2,3,'AWE'), "cam_id_thd": (32,31,88,84), "cam_id_no_thd": (1,4,87,83), "mon_id": (19,20,54,51) }

STATION = [ HOK,KOW,OLY,LAK,TSY,SUN,TUC,AIR ]

class update_log_to_SMMS:
        def __init__(self,log):
                self.log=log
        def update_log(string):
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                        ssh.connect(COMP, username=USER, password=PSW, allow_agent = False)
                except paramiko.SSHException:
                        print("Connectin Failed")
                        quit()
                print(string.log)
                print(LOGP)
                stdin,stdout,stderr = ssh.exec_command("cd " + LOGP +" && d: && echo " +  string.log  +" >> server_cmd_prg.txt")
                for line in stdout.readlines():
                        print(line.strip())
                ssh.close()

def send_url_cmd(string):
	result = urllib.request.urlopen(string)
	html = result.read().decode("UTF-8")
	print(html)
	return html

def log_file(logs):
	f = open("/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.log", "a+")
	f.write(logs + "\n")
TOM_IP = "192.168.0.171"
while 1:
	a = ser.read(100)
	print(a)
#	a = codecs.decode(ser.read(),"UTF-8") #.decode('utf-16')
	s = ''.join([chr(int(x, 16)) for x in a.split()])
	s = s.strip()
	print(s)
	if len(s) == 4 and s != 'L000':
		count_down = {"time": s[1:], "count": "down", "status": "start"}
		q_count_down = parse.urlencode(count_down)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_down
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Down Start")
		logs = html + " " + str(today) + " Time Interval Clock Down Start"
		log_file(logs)
		TIC=update_log_to_SMMS(logs)
		TIC.update_log()

	if s == 'L000':
		count_up = {"time": s[1:], "count": "up", "status": "start"}
		q_count_up = parse.urlencode(count_up)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_up
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Up Start")
		logs = html + " " + str(today) + " Time Interval Clock Up Start"
		log_file(logs)
		TIC.update_log_to_SMMS(logs)
		TIC.update_log()
	if s == 'S':
		count_stop = {"status": "stop"}
		q_count_stop = parse.urlencode(count_stop)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_stop
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Stop")
		logs = html + " " + str(today) + " Time Interval Clock Stop"
		log_file(logs)
		TIC=update_log_to_SMMS(logs)
		TIC.update_log()
	if s == 'THD-ON':
		THD_ON = {"status": "start"}
		Q_THD_ON = parse.urlencode(THD_ON)
		url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_ON
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Train Hold Start")
		logs = html + " " + str(today) + " Train Hold Start"
		log_file(logs)
		THD.update_log_to_SMMS(logs)
		THD.update_log()

	if s == 'THD-OFF':
		THD_OFF = {"status": "stop"}
		Q_THD_OFF = parse.urlencode(THD_OFF)
		url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_OFF
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Train Hold Stop")
		logs = html + " " + str(today) + " Train Hold Stop"
		log_file(logs)
		THD=update_log_to_SMMS(logs)
		THD.update_log()

	try:
		time.sleep(0.5)
#		print(s)
		if len(s) >= 5:
			print(s)
			time.sleep(0.5)
			e = "".join(s)
			subprocess.check_call(['/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.sh', str(e)])
		time.sleep(0.2)
	except ser.SerialTimeoutException:
		print('Data could not be read')
