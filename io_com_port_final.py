#!/usr/bin/python3
import serial
import time
import io
import subprocess
import configparser
config = configparser.ConfigParser()
config.read('/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf')
lp = config.get("CONF","LPORT").strip('\"')
subprocess.Popen(["socat", "pty,link=/dev/ttyS1", "tcp-listen:" +lp])
time.sleep(15) 
port = '/dev/ttyS1' 
baud = 9600

ser = serial.Serial(port, baud, timeout=1)
ser.reset_input_buffer()

year = time.asctime(time.localtime(time.time()))+'\r\n'
ser.write(year.encode())
ser.write(b'Give a Input Value:\r\n') 
while 1:
	a = ser.readline().decode('utf-8')
#	b=[chr(c) for c in a]
	try:
		c = a.rstrip('\x00')
		time.sleep(0.5)
		print(c)
		if len(c) != 0:
			print(c)
			time.sleep(0.5)
			subprocess.check_call(['/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.sh', str(c)])
		time.sleep(0.2)
	except ser.SerialTimeoutException:
		print('Data could not be read')
