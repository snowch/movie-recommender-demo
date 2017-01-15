# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.network "private_network", type: "dhcp"

  config.vm.provision "shell", inline: <<-SHELL

     wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
     echo "deb http://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list

     apt-get update
     apt-get upgrade -y

     sudo apt install -y python-pip build-essential libssl-dev virtualenv python3-dev cf-cli

     # Install bluemix tools if they aren't already installed
     if [[ ! -d ~/Bluemix_CLI ]];
     then
         cd ~
         wget -c http://public.dhe.ibm.com/cloud/bluemix/cli/bluemix-cli/Bluemix_CLI_0.4.5_amd64.tar.gz
         tar -xvzf Bluemix_CLI*.tar.gz
         cd Bluemix_CLI
         sudo ./install_bluemix_cli
     fi

     if [[ ! -d ~/movie-recommender-demo ]];
     then
        git clone https://github.com/snowch/movie-recommender-demo.git
        cd movie-recommender-demo/web_app
        virtualenv venv --python=python3.5
        source venv/bin/activate 
        pip3.5 install -f requirements.txt
     fi
   SHELL
end
