# https://www.datenreise.de/en/raspberry-pi-raspbian-update-update-jessie-to-stretch/




# Enable EAP WiFi (@FIXME should be captive portal)
sudo cp /tmp/wpa_supplicant.conf /etc/wpa_supplicant.conf
sudo cp /tmp/interfaces /etc/network/interfaces

# Install python 
sudo apt-get install python-opencv python-serial python-picamera

pip install -r requirements.txt

sudo systemctl status dhcpd.service

sudo dhclient wlan0

# Enable camera and change password
sudo raspi-config

# Copy system service.
sudo cp neocortex /etc/init.d/neocortex

sudo chmod +x /etc/init.d/neocortex
sudo update-rc.d neocortex defaults

sudo service neocortex status
sudo service neocortex start

sudo systemctl daemon-reload

# You should see the service listed and its status
sudo service --status-all

sudo bash ./project-create.sh ALPI-bot

adduser pi users 

sudo mkdir -p /srv/tmp/
sudo chgrp -R users /srv/tmp/
sudo chmod g+w /srv/tmp/
sudo mkdir -p /srv/www/
sudo chgrp -R users /srv/www/
sudo chmod g+w /srv/www/

cd /srv/git/ALPI-bot.git

sudo chgrp -R users .
sudo chmod -R g+rwX .
sudo find . -type d -exec chmod g+s '{}' +
sudo git config core.sharedRepository group

cd /srv/git/ALPI-bot.git/hooks

sudo touch post-receive

sudo chmod +x post-receive

# This file is created by the script.  Add whatevery you want to the end

# On local workstations
git remote add deploy ssh://pi@ip/srv/git/ALPI-bot.git/
git push deploy master

