# Udacity-Fullstack-Nanodegree-Project7

#On Local Computer
ssh-keygen

#Download latest packages

#On Server:
sudo apt-get update
sudo apt-get upgrade
sudo adduser grader
sudo su grader
vim .ssh/authorized_keys
    <add public key contents>
grader@ip-10-20-24-70:~$ chmod 700 .ssh
grader@ip-10-20-24-70:~$ chmod 644 .ssh/authorized_keys
    PasswordAuthentication no
touch /etc/sudoers.d/grader
ufw default deny incoming
ufw default allow outgoing
ufw status
ufw allow ssh
ufw allow 2200/tcp
ufw allow www
sudo ufw allow ntp
sudo ufw enable
ufw status
history
sudo apt-get install apache2
root@ip-10-20-24-70:~# sudo apt-get install apache2^C
root@ip-10-20-24-70:~# sudo apt-get install libapache2-mod-wsgi
apt-get install git
sudo apt-get install ntp
