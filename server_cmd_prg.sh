#!/bin/bash
source /home/c4988/git_rep/MCS_TO_Mon_Intrface/server_cmd_prg.conf
if [ $(whoami) != 'root' ]; then
        echo; echo -e "\e[1;31mScript must be run as sudo. Please Type \"sudo\" To Run As Root \e[0m"; echo
        exit 1;
fi
#socat pty,link=/dev/ttyS1 tcp-listen:$LPORT &
sleep 1
line=$1
echo ${line[*]}
#echo ${#line[@]}
sleep 1
copy_to_server()
{
exec sshpass -p $PASSWORD scp server_cmd_prg.log $USER_AT_HOST:$LOG_FILE_PATH/server_cmd_prg.txt &
}
send_cmd()
{
        case $1 in
        1)
		result=$(curl "http://$TO_MONITOR_IP_ADDR/TIC.cgi?time=123&count=up&status=start")
		echo "$result "`date` "Time Interval Clock Up Start - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
		echo "$result "`date`
        ;;
        2)      
		result=$(curl "http://$TO_MONITOR_IP_ADDR/TIC.cgi?time=123&count=down&status=start")
                echo "$result "`date`
		echo "$result "`date` "Time Interval Clock Down Start - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        3)      
		result=$(curl "http://$TO_MONITOR_IP_ADDR/TIC.cgi?status=stop")
                echo "$result "`date`
		echo "$result "`date` "Time Interval Clock Stop - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        4)      
		result=$(curl "http://$TO_MONITOR_IP_ADDR/trainhold.cgi?status=start")
                echo "$result "`date`
		echo "$result "`date` "Train Hold On - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        5)      
		result=$(curl "http://$TO_MONITOR_IP_ADDR/trainhold.cgi?status=stop")
                echo "$result "`date`
		echo "$result "`date` "Train Hold Off - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        6)      
		result=$(curl "http://$TO_MONITOR_IP_ADDR/trainap.cgi?status=start")
                echo "$result "`date`
		echo "$result "`date` "Train Approaching On - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        7)      	
		result=$(curl "http://$TO_MONITOR_IP_ADDR/trainap.cgi?status=stop")
                echo "$result "`date`
		echo "$result "`date` "Train Approaching Off - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}" >> server_cmd_prg.log
        ;;
        esac
}
#for ((i=0;i< ${#line[@]}; i++)); do

#        array_cmd="${line[$i]}"
array_cmd=$line
substr=${array_cmd:2:${#array_cmd}}

if [ ! -z $DIR/$FILE_TH_START ] && [ -f $DIR/$FILE_TH_START ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TH_START=($(cat $DIR/$FILE_TH_START))'
        length=${#TH_START[@]}
        for ((a=0; a<$length; a++)); do
                if [[ ${TH_START[$a]} == $substr ]]; then
		echo "Train Hold Start Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TrainHoldStart=4
		send_cmd "$TrainHoldStart"
		continue
		fi
	done
fi
if [ ! -z $DIR/$FILE_TH_STOP ] && [ -f $DIR/$FILE_TH_STOP ]; then
      	IFS=$'\r\n' GLOBIGNORE='*' command eval  'TH_STOP=($(cat $DIR/$FILE_TH_STOP))'
        length=${#TH_STOP[@]}
        for ((b=0; b<$length; b++)); do
      		if [[ ${TH_STOP[$b]} == $substr ]]; then
		echo "Train Hold Stop Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TrainHoldStop=5
		send_cmd "$TrainHoldStop"
		continue
		fi
	done
fi
if [ ! -z $DIR/$FILE_TIC_TIME_UP ] && [ -f $DIR/$FILE_TIC_TIME_UP ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TIC_TIME_UP=($(cat $DIR/$FILE_TIC_TIME_UP))'
        length=${#TIC_TIME_UP[@]}
        for ((c=0; c<$length; c++)); do
                if [[ ${TIC_TIME_UP[$c]} == $substr ]]; then
                echo "TIC Time Count Up Start Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TICTimeUp=1
                send_cmd "$TICTimeUp"
		continue 
                fi
        done
fi
if [ ! -z $DIR/$FILE_TIC_TIME_DOWN ] && [ -f $DIR/$FILE_TIC_TIME_DOWN ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TIC_TIME_DOWN=($(cat $DIR/$FILE_TIC_TIME_DOWN))'
        length=${#TIC_TIME_DOWN[@]}
        for ((d=0; d<$length; d++)); do
                if [[ ${TIC_TIME_DOWN[$d]} == $substr ]]; then
                echo "TIC Time Count Down Start Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TICTimeDown=2
                send_cmd "$TICTimeDown"
		continue
                fi
        done
fi
if [ ! -z $DIR/$FILE_TIC_TIME_STOP ] && [ -f $DIR/$FILE_TIC_TIME_STOP ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TIC_TIME_STOP=($(cat $DIR/$FILE_TIC_TIME_STOP))'
        length=${#TIC_TIME_STOP[@]}
        for ((e=0; e<$length; e++)); do
                if [[ ${TIC_TIME_STOP[$e]} == $substr ]]; then
                echo "TIC Time Count Stop Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TICTimeStop=3
                send_cmd "$TICTimeStop"
		continue                
                fi
        done
fi
if [ ! -z $DIR/$FILE_TRAIN_AP_START ] && [ -f  $DIR/$FILE_TRAIN_AP_START ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TRAIN_AP_START=($(cat $DIR/$FILE_TRAIN_AP_START))'
        length=${#TRAIN_AP_START[@]}
        for ((f=0; f<$length; f++)); do
                if [[ ${TRAIN_AP_START[$f]} == $substr ]]; then
                echo "Train Approach Start Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TrainApStart=6
                send_cmd "$TrainApStart"
                continue
                fi
        done
fi
if [ ! -z $DIR/$FILE_TRAIN_AP_STOP ] && [ -f $DIR/$FILE_TRAIN_AP_STOP ]; then
        IFS=$'\r\n' GLOBIGNORE='*' command eval  'TRAIN_AP_STOP=($(cat $DIR/$FILE_TRAIN_AP_STOP))'
        length=${#TRAIN_AP_STOP[@]}
        for ((g=0; g<$length; g++)); do
                if [[ ${TRAIN_AP_STOP[$g]} == $substr ]]; then
                echo "Train Approach Stop Exists - Monitor-ID: ${substr:0:2} Camara-ID: ${substr:2:3}"
                TrainApStop=7
                send_cmd "$TrainApStop"
                continue 
                fi
        done
fi
copy_to_server
