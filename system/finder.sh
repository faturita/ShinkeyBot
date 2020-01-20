/usr/local/Cellar/nmap/7.70/bin/nmap -sP 10.17.0.0/16
arp -a | grep `cat shinkeybotmacaddress`


/usr/local/Cellar/nmap/7.70/bin/nmap -p 22 --open -sV 10.17.*.* 
echo OpenSSH 6.0p1 Debian " is for Rpi

