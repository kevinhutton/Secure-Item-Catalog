# Udacity-Fullstack-Nanodegree-Project7

Server IP: 52.39.147.159
Website Address: http://52.39.147.159/
SSH User to login as: grader
SSH Key: grader
SSH Port: 2200

## SSH Login Instructions
1) git clone https://github.com/kevinhutton/Udacity-Fullstack-Nanodegree-Project7.git
2) cd Udacity-Fullstack-Nanodegree-Project7/
3) ssh -i grader grader@52.39.147.159 -p 2200

## Packages Used or Installed 
apache2
postgresql
ufw
git
Python


## Server Setup Instructions


#Download latest packages
sudo apt-get update
sudo apt-get upgrade

### Add Grader User
```
sudo adduser grader
sudo su grader
```
### Grant sudo permissions to "grader"
```
touch /etc/sudoers.d/grader
root@ip-10-20-24-70:/etc/apache2/sites-available# cat /etc/sudoers.d/grader
grader ALL=(ALL) NOPASSWD:ALL
```
### Add grader.pub contents to .ssh/authorized_keys
```
vim .ssh/authorized_keys 
cat .ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCZ2DOkrC7gwH1ERF3ivGZqK6u6rM7FaOolZlInwELI2Gq6lXHMJdOu8TjrbczQOIgkPwMow96v00L1gtw5TY8b/dJKAo7Vrx/Ohs1DiRqcfRmPR5bevB+YpPY/Jac+PM6A7rFmuFSBMtjkpQ+Jzy61f0WKnJqzaEG9u5s5clvIJ1BtcNlvCZ0DFRdI273QMwkVgSiLJik9zhxjlFlchgJoWCVSFQUgxFToNJ9I7zKGyf6DqiYyzwLxpZx3LJP1YH2WMHdi0IMyo0TFPb/lGmxjFcBMHazMJfOkH7KiTE6Oi98XKzPmrVma1PUWxYVv+XrbNtN9S5LoHlDK8pGxH1RH boxer
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCom+to7oX59y2ocd7GYiZ3s+Rtip+U6a2quTRVS3Fz2gAFk4+wKrAcHb08el7+eST3WkNU1xOSAd3vZWzJHKS9gxahE5IZFsFcFNWZ+eemfP9Y/hsfhibvqID37AfgkU0x3XOWW093hOve3lwL9M6GYYzRt7Wx9UAtK6SQ40EvL2i77H3MCmdz+qmmf23QkmnxPsYLUD0hXR/jj7et3GssrLfdXK+Ey+Uzl5V1Qf15hApJ7i7tyW+d/T83TRMyIc2OcrWh3nKaXezCamwxBlZA3p4UprN8sLZEZrZRPZSaipnbVd1CRf0vzV6H1/C8DqaB9CPHiPkyL/NeLzrG0sgj Udacity Student
$ chmod 700 .ssh
$ chmod 644 .ssh/authorized_keys
```
### Configure SSH - Disable root login , change port from 22 to 2200 , 
```
cat /etc/ssh/sshd_config  | less
[...]

Port 2200
PubkeyAuthentication yes
PasswordAuthentication no
PermitRootLogin no

```
### Configure firewall to allow connections on 2200,80,ntp
```
ufw default deny incoming
ufw default allow outgoing
ufw status
ufw allow 2200/tcp
ufw allow www
sudo ufw allow ntp
sudo ufw enable
ufw status
```

### Install apache webserver and mod-wsgi
```
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
```

### Configure Apache
```
DocumentRoot /var/www/html
RedirectMatch 404 /\.git
WSGIScriptAlias / /var/www/html/catalog/catalog.wsgi

```
### Install git and ntp
sudo apt-get install git
sudo apt-get install ntp

### Install postgresql
sudo apt-get install postgresql

### Modify postgres configuration file(pg_hba.conf) so that remote connections are not allowed / make sure everyone connects using password

Make sure other accounts login using password to access DB via "password" authentication method
```
vim /etc/postgresql/9.3/main/pg_hba.conf 
# Database administrative login by Unix domain socket
local   all             postgres                               password 

# TYPE  DATABASE        USER            ADDRESS                 METHOD
# "local" is for Unix domain socket connections only
local   all             all                                    password 
# IPv4 local connections:
host    all             all             127.0.0.1/32           password 
# IPv6 local connections:
host    all             all             ::1/128                password 

 /etc/init.d/postgresql restart


```
### Give postgres user a password
```
$ sudo su postgres -c 'psql ' 

psql (9.3.15)
Type "help" for help.

postgres=# ALTER USER "postgres" WITH PASSWORD 'postgres';
```

### Add Catalog data
 ```
 grader@ip-10-20-24-70:~$  createdb -U postgres catalog
  
```

### Setup table structure and create 'catalog' user with limited permissions
```
grader@ip-10-20-24-70:/var/www/html/catalog$ python database_setup.py
psql -U postgres
postgres=# create user catalog with password 'catalog' ; 
CREATE ROLE
postgres=# grant connect on database catalog to catalog ;
GRANT
postgres=# \connect catalog
You are now connected to database "catalog" as user "postgres".
catalog=# grant select,insert,update,delete on table category to catalog ;
GRANT
catalog=# grant select,insert,update,delete on table category_item to catalog ;
GRANT
catalog=# grant select,insert,update,delete on table users to catalog ;
GRANT
catalog=# \q

```


