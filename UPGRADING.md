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

### 6/13/16 - Upgrade Django from 1.7 to 1.9
Related Github issue: https://github.com/roundware/roundware-server/pull/283

The time has come to upgrade Django and other required apps to their newest versions. If you are
installing Roundware from scratch, there is no need to take extra steps. However, if your
installation is based on a commit prior to the Django 1.9 migration, some manual setup is needed.

#### Detailed Steps (for production machines, not vagrant)

1. Pull the relevant post-upgrade `roundware-server` commit (or newer)
2. Remove obsolete `auth_permission` rows (see issue #291):

 ```
 sudo su - postgres -c 'psql -c "DELETE FROM auth_permission WHERE id IN (SELECT id FROM auth_permission EXCEPT ((SELECT permission_id FROM auth_group_permissions) UNION (SELECT permission_id FROM auth_user_user_permissions)))" roundware'
 ```

3. Initial deploy: `sudo ./deploy.sh` (this will error on `django-guardian` but don't worry,
   we're about to fix that)
4. Run migrations

 ```
 sudo su - roundware -c "/var/www/roundware/source/roundware/manage.py migrate guardian --fake-initial"
 sudo su - roundware -c "/var/www/roundware/source/roundware/manage.py migrate"
 ```
5. Replace apache config (note this will over-write any customizations you may have made)

 ```
 sudo rm -f /etc/apache2/sites-available/roundware.conf
 sudo su - -c "sed s/USERNAME/roundware/g /var/www/roundware/source/files/etc-apache2-sites-available-roundware > /etc/apache2/sites-available/roundware.conf"
 ```
6. Run `sudo ./deploy.sh`

#### Notes / Troubleshooting

* As part of the upgrade process, [django-guardian](http://django-guardian.readthedocs.io/en/stable/)
must be updated from 1.2.4 to 1.4.4. While the old versions of guardian used `syncdb` to populate
the database, newer versions use migrations. The database structures are identical; however, these
migrations do not check if the tables and relationships are already in place. Therefore, you must
suppress guardian's initial migration.
* You might have to manually uninstall `django-chartit`. `django-chartit2` is meant
to be a drop-in replacement, but if `django-chartit` is still installed, it will not work. Ensure
that the `roundware` user can access all new `site-packages`.
* You might also need to uninstall `django-admin-bootstrapped` manually. Symptomatically, if the
Django admin panel has no theme, it's likely that an old version of `django-admin-bootstrapped` was installed globally
(`/usr/local/lib`) and is now interfering with the new `django-admin-bootstrapped` in the `virtualenv`. Old versions
required `django_admin_bootstrapped.bootstrap3` to be in `INSTALLED_APPS` to render the theme.
Otherwise, it would fail silently, and no theme would be rendered. Try running `pip freeze`;
if `django-admin-bootstrapped` is `v2.0.4`, run `pip uninstall django-admin-bootstrapped`.
* Roundware's `wsgi.py` was moved in this commit, and the Apache conf file must be updated. If you
get 404 errors after upgrading, chances are you skipped this step.
* Check the log to ensure that all of the required apps are located in `/var/www/roundware/lib/`.
It isn't necessary, but it might save you some headache with permissions.

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
2. Deploy code as necessary: `sudo ./deploy.sh`
3. Dump RW data

 ```
 sudo su - roundware -c "/var/www/roundware/source/roundware/manage.py dumpdata --all --indent=4 > ~/rw-pre-postgres.json"
 ```
4. Update server to initial postgres version before any schema changes: `git checkout post-postgres`
5. Install dependencies

 ```
 sudo apt-get install binutils libproj-dev gdal-bin postgresql-server-dev-9.3 postgresql-9.3-postgis-2.1 libgdal-dev
 sudo pip install psycopg2 geopy
 ```
6. Configure Postgres DB

 ```
 sudo su - postgres -c 'psql -c "create role round superuser login;"'
 sudo su - postgres -c 'psql -c "create database roundware"'
 sudo su - postgres -c 'psql -c "grant all on database roundware to round"'
 sudo su - postgres -c "psql -c \"alter user round password 'round'\""
 sudo su - postgres -c "psql roundware -c 'create extension postgis'"
 ```
7. Deploy code again to run pip installs and minor migration in preparation for data import: `sudo ./deploy.sh`
8. Prepare database and import fixture
 1. switch to `roundware` user in order to run `manage.py` commands: `sudo su roundware`
 2. enter virtualenv: `source /var/www/roundware/bin/activate`
 3. set PYTHONPATH: `export PYTHONPATH=/var/www/roundware/source/`
 4. Flush database to enable import w/o errors (default pw: round - CHANGE!): `(roundware)roundware@rw-server:/var/www/roundware/source/roundware$ ./manage.py sqlflush | ./manage.py dbshell`
 5. Load exported fixture: `./manage.py loaddata /path/to/rw-pre-postgres.json`
9. `exit` `roundware` user
10. Update to most recent code including speaker polygon updates: `git checkout develop`
11. Deploy newest code (includes additional pip installs and data/schema migrations): `sudo ./deploy.sh`

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
