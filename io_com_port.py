#!/usr/bin/python3
import serial
import time
import io
import subprocess

port = '/dev/ttyS2' 
baud = 9600

ser = serial.Serial(port, baud, timeout=1)
# open the serial port
#if ser.isOpen():
#	print(ser.name + ' is open...')

#while True:
#	cmd = input("Enter command of 'Exit':")
#	if cmd == 'exit':
#		ser.close()
#		exit
#	else:
#		ser.write(cmd.encode() + bytes([13, 10]))
#		out = ser.read()
#		print('Receiving ..'+out)
 
#ser_v = serial.Serial(port, 9600, timeout=1)
ser.reset_input_buffer()
time.sleep(1.5)


year = time.asctime(time.localtime(time.time()))+'\r\n'
ser.write(year.encode())
ser.write(b'Give a Input Value:\r\n') 
while 1:
	bytesToRead = ser.inWaiting()
	a = ser.read(bytesToRead) 
	try:
		a = a.decode('utf-8')
		print(a)
		a = a.rstrip()
#		hex_string = binascii.hexlify(s).decode('utf-8')
#		ser2 = serial.Serial('/dev/ttS1', 9600)
		b = a 
		time.sleep(1)
		print (a)
		l1=[c for c in b]
		l2=[ord(c) for c in b]
		if len(l2) != 0:
			l2.remove(0)
			l3=[chr(d) for d in l2] 
			cmd = "".join(l3)
			time.sleep(1.2)
			subprocess.check_call(['/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.sh', str(cmd)])
#		l3=[chr(d) for d in l2]
#		print(l3)
#		cmd = "".join(l3)
#		subprocess.check_call(['/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.sh', str(cmd)])
		time.sleep(1.2)
	except ser.SerialTimeoutException:
		print('Data could not be read')
