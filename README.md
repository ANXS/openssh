## ANXS - openssh [![Build Status](https://travis-ci.org/ANXS/openssh.png)](https://travis-ci.org/ANXS/openssh)

Ansible role which installs and configures openssh. This role will ensure that all appropriate system hostkeys will be generated the first time it is run.


#### Requirements & Dependencies
- Tested on Ansible 2.3 or higher.


#### Variables

```yaml
openssh_client_settings: ...
openssh_server_settings: ...
```

See the [defaults](defaults/main.yml) to have the complete view. Make sure, if you edit them, to copy all of them in your host/vars/... files, and change the ones that need tweaking (it's in fact only one variable, containing a map.) Alternatively, you may set your Ansible `hash_behaviour` to `merge`. You may then override simply the variables you wish to change from their defaults.


#### Testing
This project comes with a VagrantFile, this is a fast and easy way to test changes to the role, fire it up with `vagrant up`

See [vagrant docs](https://docs.vagrantup.com/v2/) for getting setup with vagrant


#### License

Licensed under the MIT License. See the LICENSE file for details.


#### Feedback, bug-reports, requests, ...

Are [welcome](https://github.com/ANXS/openssh/issues)!
