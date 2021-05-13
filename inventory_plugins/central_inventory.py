'''
Aruba Central Inventory Plugin
'''

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
    name: central_inventory
    plugin_type: inventory
    short_description: Returns Ansible inventory from YAML
    description: Returns/Generates an Ansible inventory for
                 Aruba Central from a YAML based inventory
                 plugin config file with Central credentials.
    options:
      plugin:
          description: Name of the plugin
          required: true
          choices: ["central_inventory"]
      host:
        description: Hostname for the inventory file which gets
                     generated through this plugin. Its a good practice
                     to name this parameter as "central", since
                     Aruba Central  will always be the singular host
                     for the aruba_central_role.
        required: true
      access_token:
        description: This is the Aruba Central Access token obtained
                     from the API token on Central API gateway.
                     It is valid for only 7200 seconds or 2 hours.
        required: true
      refresh_token:
        description: This is the Aruba Central Refresh token obtained
                     from the API token on Central API gateway. It is used
                     to renew an invalid access token, since access
                     token is valid only for 7200 seconds or 2 hours.
        required: true
      client_id:
        description: This is the Aruba Central Client ID obtained from
                     API token list on My Apps & Token or System Apps & Tokens
                     on Central API gateway.
        required: true
      client_secret:
        description: This is the Aruba Central Client Secret obtained from
                     API token list on My Apps & Token or System Apps & Tokens
                     on Central API gateway.
        required: true
      api_gateway:
        description: This is base url for the Aruba Central API gateway.
                     For example, for US-2 cluster the API Gateway base url
                     is apigw-prod2.central.arubanetworks.com. This base url
                     is different for different clusters.
        required: true
"""
import json
import yaml
import requests
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError

class InventoryModule(BaseInventoryPlugin):
    '''
    Custom inventory plugin class
    '''
    NAME = "central_inventory"

    def __init__(self):
        super(InventoryModule, self).__init__()
        self.inv_data = None
        self.plugin = None
        self.inventory_file = None
        self.host = None
        self.acc_tok = None
        self.ref_tok = None
        self.client_id = None
        self.client_sec = None
        self.api_gw = None

    def verify_file(self, path):
        """Return true/false if this is a
        valid file for this plugin to consume
        """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith((".yml",
                              ".yaml")):
                valid = True
        return valid

    def populate(self):
        """Return the hosts and groups"""
        try:
            self.inventory.add_host(host=self.host)
            self.inventory.set_variable(
                self.host,
                "ansible_host",
                self.api_gw)
            self.inventory.set_variable(
                self.host,
                "ansible_connection",
                "httpapi")
            self.inventory.set_variable(
                self.host,
                "ansible_network_os",
                "aruba_central")
            self.inventory.set_variable(
                self.host,
                "ansible_httpapi_use_ssl",
                True)
            self.inventory.set_variable(
                self.host,
                "ansible_httpapi_central_inv_plugin",
                True)

            if self.acc_tok is not None:

                if validate_token(self.api_gw, self.acc_tok):
                    self.inventory.set_variable(
                        self.host,
                        "ansible_httpapi_central_access_token",
                        self.acc_tok)

                elif (self.ref_tok is not None and
                      self.client_id is not None and
                      self.client_sec is not None):
                    new_acc_tok, new_ref_tok = token_renew(
                        self.api_gw,
                        self.ref_tok,
                        self.client_id,
                        self.client_sec)

                    if new_acc_tok != "changeme":
                        self.inv_data["access_token"] = new_acc_tok
                        self.inv_data["refresh_token"] = new_ref_tok
                        with open(self.inventory_file, "w") as inv:
                            new_inv_data = {
                                "api_gateway": self.api_gw,
                                "host": self.host,
                                "client_id": self.client_id,
                                "plugin": self.plugin,
                                "access_token": new_acc_tok,
                                "client_secret": self.client_sec,
                                "refresh_token": new_ref_tok}
                            yaml.dump(new_inv_data, inv)
                            self.inventory.set_variable(
                                self.host,
                                "ansible_httpapi_central_access_token",
                                new_acc_tok)

                else:
                    self.inventory.set_variable(
                        self.host,
                        "ansible_httpapi_central_access_token",
                        None)

        except Exception as err:
            raise AnsibleError(
                "Use a valid credentials in the inventory "
                "plugin config file. {}".format(err)) from None

    def parse(self, inventory, loader, path, cache=True):
        '''
        Parses the inventory config source to generate
        dynamic inventory
        '''
        super(InventoryModule, self).parse(inventory, loader, path)
        self._read_config_data(path)
        self.inv_data = {}
        self.inv_data.update(self._read_config_data(path))
        try:
            self.plugin = str(self.get_option("plugin"))
            self.inventory_file = str(path)
            self.host = str(self.get_option("host"))
            self.acc_tok = str(self.get_option("access_token"))
            self.ref_tok = str(self.get_option("refresh_token"))
            self.client_id = str(self.get_option("client_id"))
            self.client_sec = str(self.get_option("client_secret"))
            self.api_gw = str(self.get_option("api_gateway"))

        except Exception as err:
            raise AnsibleParserError(
                "Check inventory plugin config for "
                "vaild parameters: {}".format(err)) from None
        self.populate()


def token_renew(api_gateway, ref_tok, client_id, client_secret):
    '''
    Renews an expired Access Token and returns a valid one
    using a valid Refresh Token, Client ID and Client Secret.
    '''
    session = requests.Session()
    path = "/oauth2/token"
    url = "https://" + api_gateway + path
    params = {"client_id": client_id, "client_secret": client_secret,
              "grant_type": "refresh_token", "refresh_token": ref_tok}
    req = requests.Request(method="POST", url=url, params=params)
    prepped = session.prepare_request(req)
    settings = session.merge_environment_settings(prepped.url, {},
                                                  None, True, None)
    response = session.send(prepped, **settings)
    if response.status_code == 200:
        new_acc_tok = json.loads(response.text)["access_token"]
        new_ref_tok = json.loads(response.text)["refresh_token"]

    elif response.status_code != 200:
        new_ref_tok = "<ENTER_VALID_REFRESH_TOKEN>"
        new_acc_tok = "<ENTER_VALID_ACCESS_TOKEN>"

    return new_acc_tok, new_ref_tok


def validate_token(api_gateway, acc_tok):
    '''
    Checks the validity of the user provided Access Token
    '''
    valid = False
    session = requests.Session()
    headers = {"Authorization": "Bearer " + acc_tok}
    path = "/configuration/v2/groups?limit=1&offset=0"
    url = "https://" + api_gateway + path
    req = requests.Request(method="GET", url=url, headers=headers)
    prepped = session.prepare_request(req)
    settings = session.merge_environment_settings(prepped.url, {}, None,
                                                  True, None)
    response = session.send(prepped, **settings)
    if response.status_code == 200:
        valid = True
    return valid
