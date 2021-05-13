# aruba-central-ansible-role

This Ansible Network role provides a set of platform dependent configuration management modules and plugins specifically designed for Aruba Central, which is a cloud-based Network Management System.

## [](https://github.com/aruba/aruba-central-ansible-role#requirements)Requirements

* Python 3.5+
* Ansible 2.9 or later  
  * Ansible 2.10+ requires `ansible.netcommon` collection to be installed
* Minimum supported Aruba Central firmware is 2.5.2

* Install all Ansible requirements, with the following command:
    ```
    ansible-galaxy install -r requirements.yml
    ```
* Install all Python requirements with the following command:
    ```
    pip install -r requirements.txt
    ```
## [](https://github.com/aruba/aruba-central-ansible-role#installation)Installation

Through Galaxy:

```
ansible-galaxy install arubanetworks.aruba_central_role
```

Through Github, use the following command. Use option  `-f`  to overwrite current role version:

```
ansible-galaxy install git+https://github.com/aruba/aruba-central-ansible-role.git
```
## [](https://github.com/aruba/aruba-central-ansible-role#notes)Notes

- The modules in this role use Central's REST API. For information on REST API and how to obtain an access for using REST API, visit the Aruba Developer Hub: [Getting Started with REST API](https://developer.arubanetworks.com/aruba-central/docs/api-getting-started)
- An API token must be created for a user on Aruba Central's API Gateway and a valid, non-expired **`access_token`** must be used. For more information on how to get started with the API Gateway you can also watch this [YouTube Video](https://www.youtube.com/watch?v=tWEsL7zSOB0).
- A valid access token can be used in an Inventory file as mentioned in the [Inventory](https://github.com/aruba/aruba-central-ansible-role#inventory) section.
- Ensure that the access token was created with "Network Operations" selected in the Application drop-down list, while adding a new token on the API Gateway. 
- Once a new token is generated, it will have an `access_token` and a `refresh_token`.
- An access token is valid for a period of 7200 seconds or two hours. After two hours, it will expire and a new token needs to be created. The token expiry time is currently not configurable.
- The **`refresh_token`** along with the **`client_id`** and **`client_secret`** are used to renew the access token. This functionality is implemented in this role by using an Inventory Plugin. You can either use an Inventory file or use an Inventory Plugin Config file for using the plugin.
- More details on how to use this plugin config file with tokens and other credentials for auto-renew of tokens is mentioned below in the [Inventory Plugin Config File](https://github.com/aruba/aruba-central-ansible-role#inventory-plugin-config-file) section.

## [](https://github.com/aruba/aruba-central-ansible-role#inventory) Inventory/Host File
There are two ways in which you can use an inventory or host file with the Aruba Central Ansible Role:
1. **Inventory** 
    - Host file which tells Ansible the required httpapi plugin to use with some other details and the access token.
2. **Inventory Plugin Config File** or **Inventory Source**
	- A typical inventory plugin implementation has a plugin script (usually written in Python), and an inventory source (in this case it is a YAML file).
	- Based on Ansible Documentation,  Inventory sources are the input strings that inventory plugins work with. An inventory source can be a path to a file or to a script, or it can be raw data that the plugin can interpret to dynamically generate an inventory variables.
    - Only `.yml` files with below as mentioned Inventory Plugin Config File variables are accepted as an inventory source by the inventory plugin.
- You can use either type of Inventory File depending on your need. 
	- If do not require auto-renew of tokens, use the simple Inventory file
	- Or, if you wish to have the auto-renew of tokens, use an Inventory Plugin Config File for the Inventory Plugin.


## Inventory 
### [](https://github.com/aruba/aruba-cnetral-ansible-role#inventory-variables)Inventory Variables

The variables that should be defined in your inventory for your Aruba Central account are:

- `ansible_host`: Cluster-specific base URL path for API Gateway on Aruba Central in FQDN format, which can be found from the base url of the API Documentation page on API Gateway
- `ansible_connection`: Must always be set to  `httpapi`
- `ansible_network_os`: Must always be set to  `aruba_central`
- `ansible_httpapi_use_ssl`: Must always be set to  `True`
- `ansible_httpapi_central_access_token`: Aruba Central's API access token

#### [](https://github.com/aruba/aruba-central-ansible-role#sample-inventory)Sample Inventory:

##### YAML

```YAML
all:
  hosts:
    central:
      ansible_host: apigw-prod2.central.arubanetworks.com
      ansible_connection: httpapi
      ansible_network_os: aruba_central
      ansible_httpapi_use_ssl: True
      ansible_httpapi_central_access_token: CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```

##### INI

```INI
arubacentral ansible_host=apigw-prod2.central.arubanetworks.com  ansible_connection=httpapi ansible_network_os=aruba_central  ansible_httpapi_use_ssl=True  ansible_httpapi_central_access_token=CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
```

## Inventory Plugin Config File
- This is an inventory source file which is utilized by the inventory plugin to  dynamically generate an inventory  with all the options (as shown above in the simple Inventory file) required by the HttpAPI Connection Plugin.
- User needs to create a config file which has the plugin name and other central credentials.

### Caveats
- Conventionally, an Inventory Plugin can not be shipped within a role since Ansible executes the Inventory Plugin before execution of the Playbook or Role.  More information can be found on [Ansible Docs](https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html#inventory-plugins).
	- Therefore, until we publish the Aruba Central Ansible Collection, you need to perform the following workaround for using custom inventory plugin for Central with the modules of this role - which will take care of the auto-renew of tokens.

**Method 1:**
- Copy the `central_inventory.py` inventory plugin file  from [GitHub](https://raw.githubusercontent.com/aruba/aruba-central-ansible-role/master/inventory_plugins/central_inventory.py) and store it within an `inventory_plugins` directory in your playbooks directory. 
- Your playbooks directory should have the following structure:
```
playbooks_dir
+-- playbook1.yml
+-- playbook2.yml
+-- inv_src.yml
+-- inventory_plugins/
|   +-- central_inventory.py
```
- Where `**inv_src.yml**` or any other `**.yml**` file with a different name can act as the Inventory Plugin Config file. [Sample Inventory Plugin Config File](https://github.com/aruba/aruba-central-ansible-role#inventory-plugin-config-variables) and the variables it uses are given below.
- Inventory Plugin Config File should not be used with Ansible Vault since the inventory plugin needs to write the renewed tokens back to the plugin config file.
- User has to ensure that a valid Access and Refresh Token has been entered in the Inventory Plugin Config file for the first time. If both tokens are invalid, the inventory plugin will modify the file with **<Enter a Valid Access/Refresh Token>** message in the Inventory Plugin Config file.
- Central's **`refresh_token`** is valid for a period of **14 days**. If not used until 14 days, the token will be revoked and a new token has to be created. Refresh token validity is non-configurable at the moment.

**Method 2:**
- Once the role is installed,  go to the roles directory.
 ```
$ ansible-galaxy role list 

------------------output-----------------
# /home/admin/.ansible/roles
- arubanetworks.aruba_central_role, 0.2.1
 ``` 
- The role name might differ based on how you chose to install it.
- Once you have the path move the inventory plugin directory to your playbooks directory
```
$ cd /home/admin/.ansible/roles

$ cd arubanetworks.aruba_central_role
or
$ cd aruba-central-ansible-role

$ mv inventory_plugins/ <path_to_playbooks_directory>
```
### [](https://github.com/aruba/aruba-central-ansible-role#inventory-plugin-config-variables)Inventory Plugin Config Variables

The variables that should be defined in your inventory plugin config file for your Aruba Central account are:

- `access_token`: Aruba Central's API Access Token.
- `api_gateway`: Cluster-specific base URL path for API Gateway on Aruba Central in FQDN format, which can be found from the base url of the API Documentation page on API Gateway
- `client_id`: Aruba Central's API Client ID
- `client_secret`: Aruba Central's API Client Secret
- `host`: Must always be set to  `central`
- `plugin`: Must always be set to  `central_inventory`
- `refresh_token`: Aruba Central's API Refresh token



#### [](https://github.com/aruba/aruba-central-ansible-role#sample-inventory-plugin-config-file)Sample Inventory Plugin Config File:

##### YAML

```YAML
access_token: CnjDaXXxvnjrvJRwxxxxXXxxXXXXxxxx
api_gateway: apigw-prod2.central.arubanetworks.com
client_id: FOqWxx124ASdfS36HqKIeXXzZ
client_secret: O2RfdKgiS13GhswdrWAIEueMPOxxZxX
host: central
plugin: central_inventory
refresh_token: X12daE6BFhk8QqqzzeifHTYxxZZ12XxX

```

## [](https://github.com/aruba/aruba-central-ansible-role#example-playbook)Example Playbooks

### Including the Role

If role installed through  [Galaxy](https://galaxy.ansible.com/arubanetworks/aruba_central_role)  set role to  `arubanetworks.aruba_central_role`:

    ---
    -  hosts: all
       roles:
         - role: arubanetworks.aruba_central_role
       tasks:
       - name: Get all the UI and Template Groups on Central
         central_groups:
           action: get_groups
           limit: 20
           offset: 0
If role installed through  [Github](https://github.com/aruba/aruba-central-ansible-role)  set role to  `aruba-central-ansible-role`:

    ---
    -  hosts: all
       roles:
         - role: aruba-central-ansible-role
       tasks:
       - name: Get all the UI and Template Groups on Central
         central_groups:
           action: get_groups
           limit: 20
           offset: 0

  
## [](https://github.com/aruba/aruba-central-ansible-role#playbook-execution) Playbook Execution

```
ansible-playbook playbook.yml -i inventory.yml
```
- Where `inventory.yml` could either be a simple inventory file or it could be an inventory plugin config file (inventory source).
- Make sure to have the [`central_inventory.py`](https://raw.githubusercontent.com/aruba/aruba-central-ansible-role/master/inventory_plugins/central_inventory.py) in the `inventory_plugins/` directory before executing the playbook using the inventory plugin config file.

Contribution
-------

At Aruba Networks we're dedicated to ensuring the quality of our products, so if you find any
issues at all please open an issue on our [Github](https://github.com/aruba/aruba-central-ansible-role) and we'll be sure to respond promptly!

For more contribution opportunities follow our guidelines outlined in our [CONTRIBUTING.md](https://github.hpe.com/switchautomation/aruba-central-ansible-role/blob/master/CONTRIBUTING.md)

License
-------

MIT

Author Information
------------------

- Jay Pathak (@jayp193)
- Derek Wang (@derekwangHPEAruba)
