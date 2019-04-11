import os
import paramiko
COMP="192.168.0.95"
USER="sharath_km"
PSW="mallappa"
LOGP= "D:\Logs"
LOGP=LOGP.strip("\"")
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

obj = update_log_to_SMMS("sharath")
obj.update_log()
