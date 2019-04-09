#!/usr/bin/python3.7
import serial
import time
import io
import sys
import urllib
from urllib import parse
from urllib.request import urlopen
from urllib import request

from datetime import datetime

import codecs
import binascii
import subprocess
import configparser

config = configparser.ConfigParser()
config.read('/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf')
lp = config.get("CONF","LPORT").strip('\"')
TOM_IP = config.get("CONF","TO_MONITOR_IP_ADDR").strip('\"')
subprocess.Popen(["socat", "pty,link=/dev/ttyS1", "tcp-listen:" +lp])
time.sleep(15) 
port = '/dev/ttyS1' 
baud = 9600

ser = serial.Serial(port, baud, timeout=1)
ser.reset_input_buffer()
today = datetime.now()
year = time.asctime(time.localtime(time.time()))
ser.write(year.encode())
ser.write(b'Give a Input Value:\r\n')

HOK = { "platform": (1,2,3,4), "cam_id_thd": (111,108,110,109), "cam_id_no_thd": (1,1,29,30), "mon_id": (52,53,54,55) } 

def send_url_cmd(string):
	result = urllib.request.urlopen(string)
	html = result.read().decode("UTF-8")
	print(html)
	return html

def log_file(logs):
	f = open("/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.log", "a+")
	f.write(logs + "\n")

while 1:
	a = ser.read(20)
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

	if s == 'L000':
		count_up = {"time": s[1:], "count": "up", "status": "start"}
		q_count_up = parse.urlencode(count_up)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_up
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Up Start")
		logs = html + " " + str(today) + " Time Interval Clock Up Start"
		log_file(logs)

	if s == 'S':
		count_stop = {"status": "stop"}
		q_count_stop = parse.urlencode(count_stop)
		url = "http://" + TOM_IP + "/TIC.cgi?" + q_count_stop
		send_url_cmd(url)
		html = send_url_cmd(url)
		print(html + " " + str(today) + " Time Interval Clock Stop")
		logs = html + " " + str(today) + " Time Interval Clock Stop"
		log_file(logs)
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
