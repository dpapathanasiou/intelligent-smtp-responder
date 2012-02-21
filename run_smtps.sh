#!/bin/sh

# run_smtps.sh
# Start the smtp server as user daemon 
# and log the stderr and stout

smtps=`pwd`

while true
do
    logfile=`date | sed -e 's/ /_/g' | sed -e 's/:/_/g'`
    su -c "export PYTHONPATH=$PYTHONPATH:$smtps:$smtps/server:$smtps/utils:$smtps/agents; python -c 'import smtp_server; smtp_server.start()' > /tmp/smtp_server_$logfile.log 2>&1" daemon
    # error: send email and restart    
    mail -s "SMTP server error!" support@example.org < /tmp/smtp_server_$logfile.log
done

