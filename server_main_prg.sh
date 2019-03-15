#!/bin/bash
if [ $(whoami) != 'root' ]; then
	echo; echo -e "\e[1;31mScript must be run as sudo. Please Type \"sudo\" To Run As Root \e[0m"; echo
        exit 1;
fi
source server_cmd_prg.conf
socat pty,link=/dev/ttyS1 tcp-listen:$LPORT &
sleep 15
exec ./server_cmd_prg.sh
