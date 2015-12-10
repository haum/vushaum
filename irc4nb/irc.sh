#!/bin/sh

nick=botsebvallee
channel=lagnole
server=irc.freenode.net
password="password"
msg="!spaceapi state toggle"
fifo=/tmp/irccmd

rm -f $fifo
mkfifo $fifo
exec 3<> $fifo

echo "NICK $nick" > $fifo
echo "USER $nick +i * :$0" >> $fifo

trap "rm -f $fifo;exit 0" INT TERM EXIT

cat $fifo | nc $server 6667 | while read MESSAGE
do
  case "$MESSAGE" in
    PING*) echo "PONG${MESSAGE#PING}" >> $fifo;;
    *registered*)
                #echo "Registered : $MESSAGE"
                echo "PRIVMSG NickServ :identify $password" >> $fifo
                ;;
    *identified*)
                #echo "Identified : $MESSAGE"
                echo "JOIN #$channel" >> $fifo
                ;;
    *+v*)
                echo "PRIVMSG #$channel :${msg}" >> $fifo
                echo "QUIT" >> $fifo
                #echo "Exit 0"
                rm -f $fifo
                kill $(ps -o pid= --ppid $$)
                ;;
    *) #echo "Message : ${MESSAGE}"
                ;;
  esac
done


exit 0

