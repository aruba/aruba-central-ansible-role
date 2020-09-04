#!/usr/bin/python3
'''
Module utility to connect with Aruba Central
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

import json
from ansible.module_utils.connection import Connection
from ansible.module_utils.six.moves.urllib.parse import urlencode


class HttpHelper(object):
    def __init__(self, module):
        self._module = module
        self._connection_obj = None

    @property
    def _connection(self):
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)
        return self._connection_obj

    def http_request(self, path, method, data={}, headers={}, filename=None):
        if filename:
            return self._connection.send_file(path=path, method=method,
                                              filename=filename)

        if data:
            data = json.dumps(data)
        return self._connection.send_request(data=data, method=method,
                                             path=path, headers=headers)


class CentralApi(HttpHelper):
    def __init__(self, module):
        super(CentralApi, self).__init__(module)
        self.module = module

    def get_url(self, path, params=None):
        if params:
            return path + '?' + urlencode(params)
        else:
            return path

    def get_headers(self, file=False, method="get"):
        if file and method == "get":
            headers = {"Accept": "multipart/form-data"}
        elif file and method != "get":
            headers = {}
        elif not file and method != "get":
            headers = {"Content-Type": "application/json"}
        else:
            headers = {"Content-Type": "application/json"}

        return headers

    def get_list_params(self, params_list):
        params_str = ""
        if params_list:
            for ele in params_list:
                params_str = params_str+ele+","
                if ele == params_list[-1]:
                    params_str = params_str[:-1]
            return params_str
        else:
            return params_list

    def get(self, path, headers):
        res, code = self.http_request(path=path, method="GET", headers=headers)
        result = {'resp': res, 'code': code}
        return result

    def post(self, path, headers, data={}, filename={}):
        res, code = self.http_request(path=path, method="POST",
                                      headers=headers, data=data,
                                      filename=filename)
        result = {'resp': res, 'code': code}
        return result

    def delete(self, path, headers, data={}):
        res, code = self.http_request(path=path, headers=headers,
                                      method="DELETE", data=data)
        result = {'resp': res, 'code': code}
        return result

    def patch(self, path, headers={}, data={}, filename={}):
        res, code = self.http_request(path=path, method="PATCH",
                                      headers=headers, data=data,
                                      filename=filename)
        result = {'resp': res, 'code': code}
        return result

    def put(self, path, headers={}, data={}, filename={}):
        res, code = self.http_request(path=path, method="PUT", headers=headers,
                                      data=data, filename=filename)
        result = {'resp': res, 'code': code}
        return result
