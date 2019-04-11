import paramiko
HOST_IP="192.168.0.95"
USER_NAME="sharath_km"
PASSWORD="mallappa"

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
		stdin,stdout,stderr = ssh.exec_command("cd D:\Logs && d: && echo" + string.log +" >> server_cmd_prg.txt")
		for line in stdout.readlines():
			print(line.strip())
		ssh.close()
