#!/usr/bin/python3
'''
Ansible httpapi plugin to connect with Aruba Central
'''

# MIT License
#
# Copyright (c) 2020 Aruba, a Hewlett Packard Enterprise company
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import requests
import json
from ansible.module_utils._text import to_text
from ansible.plugins.httpapi import HttpApiBase

DOCUMENTATION = """
---
author: Aruba Networks
httpapi: aos
short_description: Use REST to interact with Aruba Central over REST API
description:
  - This Aruba Ansible plugin enables REST interactions with Aruba Central
    and the various devices managed by it
version_added: 2.8.1
options:
  access_token:
    type: str
    description:
      - This is the Aruba Central Access token obtained from the API token on
        Central API gateway
    vars:
      - name: ansible_httpapi_session_key
        version_added: '2.9'
"""


class HttpApi(HttpApiBase):
    def __init__(self, *args, **kwargs):
        super(HttpApi, self).__init__(*args, **kwargs)
        self.retry = 0
        self.access_token = None
        self.url = None

    def login(self, username, password):
        try:
            access_token = self.get_option("access_token").decode("UTF-8")
        except Exception:
            raise Exception("Missing access token! Please provide"
                            " ansible_httpapi_session_key in the inventory!")
        self.access_token = access_token
        self.connection._auth = {"Authorization": "Bearer " +
                                                  self.access_token}

    def send_file(self, path, method, filename):
        if not self.connection._connected:
            self.connection._connect()
        host = self.connection.get_option('host')
        protocol = 'https' if self.connection.get_option('use_ssl') else 'http'
        self.url = '%s://%s%s' % (protocol, host, path)
        verify = self.connection.get_option('validate_certs')
        headers = {"Authorization": "Bearer " + self.access_token}
        files = {}
        if "template_variables" in path:
            files = {"variables": open(filename, "rb")}
        elif "templates" in path:
            files = {"template": open(filename, "rb")}
        session = requests.Session()
        req = requests.Request(method=method, url=self.url, headers=headers,
                               files=files)
        prepped = session.prepare_request(req)
        settings = session.merge_environment_settings(prepped.url, {}, None,
                                                      verify, None)
        response = session.send(prepped, **settings)
        response_data = response.text
        return response_data, response.status_code

    def send_request(self, data, headers, **message_kwargs):
        if not self.connection._connected:
            self.connection._connect()
        headers['Authorization'] = "Bearer " + self.access_token
        path = message_kwargs['path']
        method = message_kwargs['method']

        response, response_data = self.connection.send(data=data,
                                                       headers=headers,
                                                       path=path,
                                                       method=method)
        try:
            if "Accept" in headers and headers["Accept"] == "application/json":
                response_data = json.loads(to_text(response_data.read()))
            else:
                response_data = response_data.read()
        except ValueError:
            response_data = response_data.read()
        except AttributeError as arr:
            raise Exception(str(response) + str(arr))
        return self.handle_response(response, response_data)

    def handle_response(self, response, response_data):
        if response and response_data:
            return response_data, response.code
