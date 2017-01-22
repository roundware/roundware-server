# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "https://cloud-images.ubuntu.com/xenial/current/xenial-server-cloudimg-amd64-vagrant.box"
  config.vm.hostname = "roundware-server"

  # Configure Apache port 80 to forward to host 8080
  config.vm.network "forwarded_port", guest: 80, host: 8080
  # Configure IceCast port 8000 to forward to host 8000
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  # Configure manage.py runserver port 8888 to forward to host 8888
  config.vm.network "forwarded_port", guest: 8888, host: 8888
  config.vm.network "forwarded_port", guest: 5432, host: 15432
    config.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
    end
  config.vm.provision "shell",
    inline: "cd /vagrant; ./install.sh"

  if Vagrant.has_plugin?("vagrant-cachier")
    # Configure cached packages to be shared between instances of the same base box.
    # More info on http://fgrehm.viewdocs.io/vagrant-cachier/usage
    config.cache.scope = :box

  end
end

