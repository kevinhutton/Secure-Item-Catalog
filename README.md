# Udacity-Fullstack-Nanodegree-Project7


# On local computer , generate grader and grader.pub keypair for ssh access to server
ssh-keygen

#Download latest packages
sudo apt-get update
sudo apt-get upgrade

# Add Grader User
sudo adduser grader
sudo su grader
# Grant sudo permissions to "grader"
touch /etc/sudoers.d/grader

# Add grader.pub contents to .ssh/authorized_keys
vim .ssh/authorized_keys && <add public key contents>
$ chmod 700 .ssh
$ chmod 644 .ssh/authorized_keys

# Configure SSH - Disable root login , change port from 22 to 2200 , 
#Configure firewall to allow connections on 2200,80,ntp
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

# Install apache webserver and mod-wsgi
sudo apt-get install apache2
root@ip-10-20-24-70:~# sudo apt-get install apache2^C
root@ip-10-20-24-70:~# sudo apt-get install libapache2-mod-wsgi

# Configure Apache
# Install git 
sudo apt-get install git
sudo apt-get install ntp
# Install postgresql
sudo apt-get install postgresql

#Modify postgres configuration file(pg_hba.conf) so that remote connections are not allowed
## Make sure that the postgres admin can only access psql if logged in via the "peer" method 
## Make sure other accounts login using password to access DB via "password" authentication method

vim /etc/postgresql/9.3/main/pg_hba.conf 
vim /etc/init.d/postgresql restart

## Give postgres user password
$ sudo su postgres -c 'psql ' 

psql (9.3.15)
Type "help" for help.

postgres=# ALTER USER "postgres" WITH PASSWORD 'postgres';

## Add Catalog data
  grader@ip-10-20-24-70:~$  createdb -U postgres catalog
  

# Setup table structure 

grader@ip-10-20-24-70:/var/www/html/catalog$ python database_setup.py
postgres=#create user catalog with password 'catalog' ;
postgres=# grant all  privileges on database catalog to catalog ;

catalog=# grant select,insert,update,delete on table category to catalog ; 
GRANT
catalog=# grant select,insert,update,delete on table category_item to catalog ; 
GRANT
catalog=# grant select,insert,update,delete on table user to catalog ; 
ERROR:  syntax error at or near "user"
LINE 1: grant select,insert,update,delete on table user to catalog ;
                                                   ^
catalog=# grant select,insert,update,delete on table "user" to catalog ; 
GRANT



