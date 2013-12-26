#!/bin/sh

# run_smtps.sh
# Start the smtp server as user daemon 
# and log the stderr and stout

smtps=`pwd`

counter=0
while true
do
    logfile=`date | sed -e 's/ /_/g' | sed -e 's/:/_/g'`
    su -c "export PYTHONPATH=$PYTHONPATH:$smtps:$smtps/server:$smtps/utils:$smtps/agents; python -c 'import smtp_server; smtp_server.start()' > /tmp/smtp_server_$logfile.log 2>&1" daemon

    # error: send email (only once every 10 restarts) and attempt to restart
    notifycheck=`expr $counter % 10`
    if [ $notifycheck -eq 0 ]
    then
        mail -s "SMTP server error! $counter restarts attempted" support@example.org < /tmp/smtp_server_$logfile.log
    fi

    counter=`expr $counter + 1`
    sleep 10
done

