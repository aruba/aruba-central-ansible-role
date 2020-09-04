# aruba-central-ansible-role

This Ansible Network role provides a set of platform dependent configuration management modules specifically designed for  Aruba Central, which a cloud-based Network Management System.

## [](https://github.com/aruba/aruba-central-ansible-role#requirements)Requirements

-   Python 2.7 or 3.5+
-   Ansible 2.9.0 or later
-   Minimum supported Aruba Central firmware version 2.5.2


## [](https://github.com/aruba/aruba-central-ansible-role#notes)Notes
-   The Aruba Central Ansible modules use Central's REST API. For information on REST API and instructions for obtaining an access to the REST API, see the Developer Hub pages in the Aruba Central REST API section, beginning with [Getting Started with REST API](https://developer.arubanetworks.com/aruba-central/docs/getting-started)
-   An API token must be created for a user on Aruba Central and a valid, non-expired **access_token** must be present
-   Ensure that the access token was created with "Network Operations" selected in the Application drop-down list. 
-   An access token is valid for a period of 7200 seconds or two hours. After two hours, it will expire and a new token needs to be created. The token expiry time is currently not configurable.

## [](https://github.com/aruba/aruba-central-ansible-role#installation)Installation

Through Github, use the following command. Use option  `-f`  to overwrite current role version:

```
ansible-galaxy install git+https://github.com/aruba/aruba-central-ansible-role.git
```

Through Galaxy:

```
ansible-galaxy install arubanetworks.aruba_central_role
```

Additionally, you'll need to install the `requests` library. You can do so with the following command: 
```
pip install -r requirements.txt
```

## [](https://github.com/aruba/aos-wlan-ansible-role#inventory-variables)Inventory Variables

The variables that should be defined in your inventory for your Aruba Central account are:

-   `ansible_host`: Base URL path for API-gateway on Aruba Central in FQDN format
-   `ansible_connection`: Must always be set to  `httpapi`
-   `ansible_network_os`: Must always be set to  `aruba_central`
-   `ansible_httpapi_use_ssl`: Must always be set to  `True`
-   `ansible_httpapi_session_key`: Aruba Central's API access token

### [](https://github.com/aruba/aos-wlan-ansible-role#sample-inventories)Sample Inventories:

##### YAML
```YAML
all:
  hosts:
    central:
      ansible_host: internal-apigw.central.arubanetworks.com
      ansible_connection: httpapi
      ansible_network_os: aruba_central
      ansible_httpapi_use_ssl: True
      ansible_httpapi_session_key: CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```

##### INI

```INI
arubacentral ansible_host=internal-apigw.central.arubanetworks.com  ansible_connection=httpapi ansible_network_os=aruba_central  ansible_httpapi_use_ssl=True  ansible_httpapi_session_key=CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```

## [](https://github.com/aruba/aruba-central-ansible-role#example-playbook)Example Playbooks

### Including the Role

If role installed through  [Github](https://github.com/aruba/aruba-central-ansible-role)  set role to  `aruba-central-ansible-role`:

    ---
    -  hosts: all
       roles:
        - role: aruba-central-ansible-role
       tasks:
         - name: Get all the UI and Template Groups on Central
		   central_groups:
		     action: get
		     limit: 20
		     offset: 0

If role installed through  [Galaxy](https://galaxy.ansible.com/arubanetworks/aruba_central_role)  set role to  `arubanetworks.aruba_central_role`:

    ---
    -  hosts: all
       roles:
        - role: arubanetworks.aos_wlan_role
       tasks:
         - name: Get all the UI and Template Groups on Central
		   central_groups:
		     action: get
		     limit: 20
		     offset: 0


Contribution
-------
At Aruba Networks we're dedicated to ensuring the quality of our products, so if you find any
issues at all please open an issue on our [Github](https://github.com/aruba/aoscx-ansible-role) and we'll be sure to respond promptly!

For more contribution opportunities follow our guidelines outlined in our [CONTRIBUTING.md](https://github.com/aruba/aoscx-ansible-role/blob/master/CONTRIBUTING.md)

License
-------

Apache 2.0

Author Information
------------------

-   Jay Pathak (@jayp193)
-   Derek Wang (@derekwangHPEAruba)
