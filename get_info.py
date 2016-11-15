#!/usr/bin/env python
#
# Copyright (c) 2016, PagerDuty, Inc. <info@pagerduty.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of PagerDuty Inc nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL PAGERDUTY INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import requests

ACCESS_TOKEN = 'gtp8FTSxyuNpiA_PYtv7'


def pd_get(endpoint, payload=None):
    """Handle all PagerDuty GET requests"""

    url = 'https://api.pagerduty.com{endpoint}'.format(endpoint=endpoint)
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Content-type': 'application/json',
        'Authorization': 'Token token={token}'.format(token=ACCESS_TOKEN)
    }
    r = requests.get(url, params=payload, headers=headers)
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception(
            'There was an issue with your GET request:\nStatus code: {code}\
            \nError: {error}'.format(code=r.status_code, error=r.text)
        )


def list_users():
    """List all users in the account"""

    output = pd_get('/users', {'limit': 100})
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/users', {'limit': 100, 'offset': offset})
            output['users'] = output['users'] + r['users']
            offset += 100
    return output

if __name__ == '__main__':
    print len(list_users()['users'])
