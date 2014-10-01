# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Vagrant Cloud name for Ubuntu 14.04 LTS
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.hostname = "roundware-server"

  # Configure Apache port 80 to forward to host 8080
  config.vm.network "forwarded_port", guest: 80, host: 8080
  # Configure IceCast port 8000 to forward to host 8000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  # Configure manage.py runserver port 8888 to forward to host 8888
  config.vm.network "forwarded_port", guest: 8888, host: 8888

  config.vm.provision "shell",
    inline: "cd /vagrant; ./install.sh"
end
