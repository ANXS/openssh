# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure('2') do |config|
  config.vm.define 'anxs' do |c|
    c.vm.box = 'ubuntu/trusty64'
    c.vm.hostname = 'anxs.local'
    c.vm.provision 'ansible' do |ansible|
      ansible.playbook = 'vagrant/test.yml'
      ansible.sudo = true
      ansible.host_key_checking = false
    end
  end
end
