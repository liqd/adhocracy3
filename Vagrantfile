# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

PROVISION_ROOT = <<eos
  echo "Installing Adhocracy 3 dependencies ..."
  apt-get update
  apt-get dist-upgrade -y
  apt-get -y install python python-setuptools ruby-dev build-essential libbz2-dev libyaml-dev libncurses5-dev libreadline6-dev zlib1g-dev libssl-dev libjpeg62-dev vim git graphviz
eos

PROVISION_USER = <<eos
  cd adhocracy3
  git submodule update --init

  echo "Compiling Python 3.4.x ..."
  cd python
  python ./bootstrap.py
  bin/buildout

  # WORKAROUND: We're manually creating a softlink and rerun buildout, because:
  #
  # 1. Hard links aren't working in VirtualBox shared folders
  # https://www.virtualbox.org/ticket/818
  #
  # 2. Python distutils requires hard links
  # http://bugs.python.org/issue8876
  #
  cd parts/opt/bin
  ln -s python3.4m python3.4
  cd -
  bin/buildout

  yes | bin/install-links
  cd ..

  echo "Installing Adhocracy 3 ..."
  bin/python3.4 ./bootstrap.py
  bin/buildout

  echo
  echo "Adhocracy installed! You may now want to run:"
  echo
  echo "vagrant ssh"
  echo "cd adhocracy3"

  echo "bin/supervisord"
  echo "bin/supervisorctl start adhocracy:*"
  echo "bin/py.test_run_all"
eos

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "trusty_64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]
  end

  # NOTE: Disk I/O is really slow in shared folders! This is a serious blocker
  # for Adhocracy development within a VirtualBox.
  #
  # Alternatives to shared folders:
  # - Use development tools like editor, git etc. inside the VM
  # - Use NFS, much faster - https://i.imgur.com/BoEBc1X.png - but possibly
  #   other problems.
  #
  config.vm.synced_folder ".", "/home/vagrant/adhocracy3"

  config.vm.network :forwarded_port, guest: 6541, host: 6541
  config.vm.network :forwarded_port, guest: 6551, host: 6551
  config.vm.network :forwarded_port, guest: 6561, host: 6561

  config.vm.provision :shell, inline: PROVISION_ROOT
  config.vm.provision :shell, inline: PROVISION_USER, :privileged => false

  # Optional settings

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network
end
