import paramiko
import configparser

config = configparser.ConfigParser()
config.read('/home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf')

COMP =config.get("SMMS_INFO","HOST_IP").strip("\"")
USER =config.get("SMMS_INFO","USER_NAME").strip("\"")
PSW =config.get("SMMS_INFO","PASSWORD").strip("\"")
LOGP =config.get("SMMS_INFO","LOG_FILE_PATH").strip('\"')
#LOGP=LOGP.strip("\"")


print(COMP,USER,PSW,LOGP)
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

obj = update_log_to_SMMS("This is working!")
obj.update_log()
