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
The following instructions describe modifications to the standard upgrade process required due to
specific changes. Items are listed in reverse chronological order.

### 3/7/16 - Convert from MySQL to Postgresql for GIS speaker upgrades
Related Github issue: https://github.com/roundware/roundware-server/pull/270

In order to expand the GIS capabilities of Roundware and take advantage of many built-in GIS
features of Django, an upgrade to Postgresql was necessary. Obviously, this is a big change
to the back-end, so there are a number of steps required which will update the dependencies,
the installation process and run both schema and data migrations.

#### Basic Process Overview
1. Dump data to fixture using django `dumpdata` from most recent MySQL-based commit
2. Update to initial Postgres commit, update dependencies and `loaddata` fixture
3. Update to newest Postgres commit and perform data and schema migrations

#### Detailed Steps

1. Update to final MySQL-based commit: `git checkout pre-postgres`
2. Dump RW data

 ```
 sudo su - roundware -c "/var/www/roundware/source/roundware/manage.py dumpdata rw > ~/rw-pre-postgres.json"
 ```
3. Update server to initial postgres version before any schema changes: `git checkout post-postgres`
4. Install dependencies

 ```
 sudo apt-get install binutils libproj-dev gdal-bin postgresql-server-dev-9.3 postgresql-9.3-postgis-2.1 libgdal-dev
 sudo pip install psycopg2 geopy
 ```
5. Configure Postgres DB

 ```
 sudo su - postgres -c 'psql -c "create role round superuser login;"'
 sudo su - postgres -c 'psql -c "create database roundware"'
 sudo su - postgres -c 'psql -c "grant all on database roundware to round"'
 sudo su - postgres -c "psql -c \"alter user round password 'round'\""
 sudo su - postgres -c "psql roundware -c 'create extension postgis'"
 ```
6. Run migration required for Postgres update: `python manage.py migrate`
7. Import dumped db from MySQL into Postgres db: `python manage.py loaddata rw-pre-postgres.json`
8. Update to most recent code including speaker polygon updates: `git checkout develop`
9. Deploy newest code (includes pip installs and db migrations): `sudo ./deploy.sh`

### 3/12/15 - Convert MyISAM tables to InnoDB
Related Github issue: https://github.com/roundware/roundware-server/pull/217

MySQL <5.5 defaulted to creating MyISAM tables. MySQL 5.5+ defaults to InnoDB. Older Roundware
installs can have a mixture of MyISAM and InnoDB tables due to this change. This will result in
MySQL errors during `manage.py migrate`. See https://code.djangoproject.com/ticket/18256 for more
details.

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

### 2/2/15 - Symlink ~/roundware-server to Production Code
Related Github issue: https://github.com/roundware/roundware-server/pull/210

Django migrations didn't run while using the `roundware` user (Note: `vagrant` user is used on
development VMs.) The issue was `install.sh` was making another copy of the code base for the
`roundware` user, but `deploy.sh` was never updating it. The solution is for `~/roundware-server`
to always be symbolic link. On development VMs `~/roundware-server` links to `/vagrant` and on
production systems it links to `/var/www/roundware/source/`. The `roundware` or `vagrant` user
`.profile` deferences the symbolic link to create the PYTHON_PATH environment variable.

```bash
sudo rm -rf /home/roundware/roundware-server/
sudo ln -snf /var/www/roundware/source/ /home/roundware/roundware-server
```

### 2/2/15 - External Production Settings
Related Github issue: https://github.com/roundware/roundware-server/pull/209

The production Roundware/Django settings file used by WSGI Apache2 is now stored outside of the
source code directory in the file `/var/www/roundware/settings/roundware_production.py`. All
settings in `/var/www/roundware/source/roundware/settings/common.py` can be overridden there. Do not modify any file within the `/var/www/roundware/source` directory.

```bash
cd roundware-server
git pull
sudo mkdir /var/www/roundware/settings
sudo cp files/var-www-roundware-settings.py /var/www/roundware/settings/roundware_production.py
sudo chown roundware:roundware -R /var/www/roundware/settings
sudo ./deploy.sh
```
