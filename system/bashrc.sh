# This code can be added to .bashrc

echo Welcome to AlpiBot
if ! pgrep python; then
    echo 'Starting AlpiBot'
    cd /srv/www/
    cd ALPI-bot
    killall -q pytjon 
    rm -f running.wt
    python Brainstem.py >> brainstem.log &
else
    echo 'AlpiBot is already running.'
fi
