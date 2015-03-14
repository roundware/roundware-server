# Upgrading Roundware Server
This document contains instructions and change notes related to upgrading Roundware Server.
Significant efforts have been made to make the upgrade process seamless, but there may be issues at
some times. Always backup your database and rwmedia directory before performing a code upgrade.

## Standard Upgrade Process
The primary upgrade process involves logging on the server, updating the code repository, and
deploying the changes. The following is the process for a Vagrant-based VM when using a clone of
https://github.com/roundware/roundware-server.git; YMMV for production servers.
```bash
user@local ~/roundware-server $ git pull
user@local ~/roundware-server $ vagrant ssh
(roundware)vagrant@roundware-server:~$ cd roundware-server
(roundware)vagrant@roundware-server:~$ sudo ./deploy.sh
```
Done!

## Change Specific Instructions
The following instructions describe modifications to the standard upgrade process required due to specific changes. Items are listed in reverse chronological order.

### 3/12/15 - Convert MyISAM tables to InnoDB
MySQL <5.5 defaulted to creating MyISAM tables. MySQL 5.5+ defaults to InnoDB. Older Roundware
installs can have a mixture of MyISAM and InnoDB tables due to this change. This will result in
MySQL errors during `manage.py migrate`. See https://code.djangoproject.com/ticket/18256 for more details.

Run the following to check the table engines used in your database:
```
(roundware)vagrant@roundware-server:~$ mysql -uround -pround -e "SELECT TABLE_NAME, ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'roundware';"
```

If the output of that command shows *any* table engine is MyISAM, then you must convert those
tables to InnoDB *before* upgrading/deploying new code. This is a simple method to convert all
tables in the Roundware Database using a single command:

```
(roundware)vagrant@roundware-server:~$ mysql -uround -pround roundware -e "SHOW TABLE STATUS WHERE Engine='MyISAM';" | awk 'NR>1 {print "ALTER TABLE "$1" ENGINE = InnoDB;"}' | mysql -uround -pround roundware
```
