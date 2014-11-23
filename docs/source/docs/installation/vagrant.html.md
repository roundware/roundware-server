---
page_title: "Vagrant"
sidebar_current: "installation-vagrant"
---

# Vagrant Install

A VagrantFile is included for local development and testing with [Vagrant](http://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/). Usage:

```
user@local-machine:~ $ git clone https://github.com/hburgund/roundware-server.git
user@local-machine:~ $ cd roundware-server
user@local-machine:~/roundware-server $ vagrant up
user@local-machine:~/roundware-server $ vagrant ssh
(roundware)vagrant@roundware-server:~$ ./runserver.sh
```

Notes:

 * The installation process uses the default *vagrant* user as project owner.
 * The install script relies on the Vagrant default fileshare of host:~/roundware-server to vm:/vagrant for installation and development.
 * There are multiple port forwards from the host to the VM:
   * VM:80->host:8080 for Apache hosting the demo "live" environment available at http://127.0.0.1:8080/
   * VM:8888->host:8888 for the manage.py runserver development webserver available at http://127.0.0.1:8888/
   * VM:8000->host:8000 for Icecast.
 * Initialize the test Roundware stream at: http://127.0.0.1:8888/api/1/?operation=request_stream&session_id=2891 then access it with an audio stream player at: http://127.0.0.1:8000/stream2891.mp3
 * Edit the development environment code on your local machine, then refresh to see the changes reflected in the virtual machine.
