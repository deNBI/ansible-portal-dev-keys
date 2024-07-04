# set_portal_dev_team_keys Ansible Role

This Ansible role automates the setup of SSH keys for team members on a target machine using the `set_portal_dev_team_keys.py` script.

## Installation
```yaml

roles:
  - name: set_portal_dev_team_keys
    src: https://github.com/deNBI/ansible-portal-dev-keys.git
    scm: git
```

~~~bash
ansible-galaxy install -r requirements.yml
~~~

## Usage
```yaml
---
roles:
  - name: set_portal_dev_team_keys
```

### Optional Parameters
By default, the role runs the set_portal_dev_team_keys.py script without the --replace parameter. To enable --replace, set the replace variable to true as shown above.