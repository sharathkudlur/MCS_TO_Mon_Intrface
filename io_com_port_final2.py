#!/usr/bin/python3.7
import serial
import time
import io
import os
import sys
import urllib
from urllib import parse
from urllib.request import urlopen
from urllib import request
import paramiko
import re

from datetime import datetime

import codecs
import binascii
import subprocess
import configparser
from configparser import ConfigParser

config = configparser.ConfigParser()
config.read('/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf')
# Load the configuration file
cwd = os.getcwd()
with open(cwd+"/server_cmd_prg.conf") as f:
	sample_config = f.read()
config = configparser.RawConfigParser(allow_no_value=True)
config.read_string(sample_config)

lp = config.get("CONF","LPORT").strip('\"')

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
#	print(LOGP)
	stdin,stdout,stderr = ssh.exec_command("cd " + LOGP +" && d: && echo \"" +  log_str  +"\" >> server_cmd_prg.txt")
	for line in stdout.readlines():
		print(line.strip())
	ssh.close()

#TOM_IP_4 = config.get("PLATFORM_4","TO_MONITOR_IP_ADDR").strip('\"')

subprocess.Popen(["socat", "pty,link=/dev/ttyS1", "tcp-listen:" +lp])

time.sleep(5) 
port = '/dev/ttyS1' 
baud = 9600

ser = serial.Serial(port, baud, timeout=1)
ser.reset_input_buffer()
today = datetime.now()
year = time.asctime(time.localtime(time.time()))
ser.write(year.encode())
#ser.write(b'Give a Input Value:\r\n')

L_PLATFORM = [ 1,2,3,4,5,6,7,8,9 ]

def send_url_cmd(string):
	result = urllib.request.urlopen(string)
	html = result.read().decode("UTF-8")
	print(html)
	return html

def log_file(logs):
	f = open(cwd+"/server_cmd_prg.log", "a+")
	f.write(logs + "\n")

def PLATFORM_TOM_IP(PLATFORM):
	for section in config.sections():
		print(section)
	for i in PLATFORM.split():
		for j in L_PLATFORM:
			if i in str(j):
				TOM_IP = config.get("PLATFORM_"+i ,"TO_MONITOR_IP_ADDR").strip('\"')
				print(TOM_IP)
				return TOM_IP
			else:
				print("Platform ip not found in config file.")
#TOM_IP="192.168.0.171"
while 1:
	a = ser.read(100)
	print(a)
#	a = codecs.decode(ser.read(),"UTF-8") #.decode('utf-16')
	s = ''.join([chr(int(x, 16)) for x in a.split()])
	s = s.strip()
#	for i in s.split():
		
#	if (re.search('L'+[0-9][0-9][1-9]),s):
	if len(s) == 4 and s != 'L000':
		count_down = {"time": s[1:], "count": "down", "status": "start"}
		q_count_down = parse.urlencode(count_down)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_down
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Down Start")
		logs = html + " " + str(today) + " Time Interval Clock Down Start"
		log_file(logs)
		update_log_to_SMMS(logs)

	if (s.find('L000') != -1):
		count_up = {"time": s[1:], "count": "up", "status": "start"}
		q_count_up = parse.urlencode(count_up)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_up
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Up Start")
		logs = html + " " + str(today) + " Time Interval Clock Up Start"
		log_file(logs)
		update_log_to_SMMS(logs)

	if (s.find('S') != -1):
		count_stop = {"status": "stop"}
		q_count_stop = parse.urlencode(count_stop)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_stop
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Stop")
		logs = html + " " + str(today) + " Time Interval Clock Stop"
		log_file(logs)
		update_log_to_SMMS(logs)

	if (s.find('THD-ON') != -1):
		THD_ON = {"status": "start"}
		Q_THD_ON = parse.urlencode(THD_ON)
		TOM_IP = PLATFORM_TOM_IP(s)
		url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_ON
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Train Hold Start")
		logs = html + " " + str(today) + " Train Hold Start"
		log_file(logs)
		update_log_to_SMMS(logs)

	if (s.find('THD-OFF') != -1):
		THD_OFF = {"status": "stop"}
		Q_THD_OFF = parse.urlencode(THD_OFF)
		TOM_IP = PLATFORM_TOM_IP(s)
		url = "http://" + TOM_IP + "/trainhold.cgi?" + Q_THD_OFF
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Train Hold Stop")
		logs = html + " " + str(today) + " Train Hold Stop"
		log_file(logs)
		update_log_to_SMMS(logs)

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
