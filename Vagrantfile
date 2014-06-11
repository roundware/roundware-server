# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise64"
  # URL for Ubuntu Server 12.04 LTS (Precise Pangolin) daily
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.hostname = "roundware-server"

  # Configure Apache port 80 to forward to host 8080
  config.vm.network "forwarded_port", guest: 80, host: 8080
  # Configure IceCast port 8000 to forward to host 8000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  # Configure IceCast port 8000 to forward to host 8000
  config.vm.network "forwarded_port", guest: 8001, host: 8001

  config.vm.provision "shell",
    inline: "cd /vagrant; ./install.sh"
end
