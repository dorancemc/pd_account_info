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
import json
from datetime import datetime, timedelta

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
        raise Exception('GET request failed with status {code}'.format(
            code=r.status_code
        ))


def list_users(team_id=None):
    """List all users in the account"""

    output = pd_get('/users', {
        'limit': 100,
        'include[]': ['contact_methods'],
        'team_ids[]': [team_id]
    })
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/users', {
                    'limit': 100,
                    'offset': offset,
                    'include[]': ['contact_methods'],
                    'team_ids[]': [team_id]
                })
            output['users'] = output['users'] + r['users']
            offset += 100
    return output


def parse_user_info(users):
    """Parse relevant user info for reporting"""

    output = []
    for user in users:
        contact_methods = []
        for i, method in enumerate(user['contact_methods']):
            contact_methods.append({
                'label': method['label'],
                'type': method['type'],
                'id': method['id']
            })
            if method['type'] == 'push_notification_contact_method':
                contact_methods[i]['address'] = 'N/A'
            elif method['type'] == 'email_contact_method':
                contact_methods[i]['address'] = method['address']
            else:
                contact_methods[i]['address'] = '{country}+{address}'.format(
                    country=method['country_code'],
                    address=method['address']
                )
        output.append({
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'contact_methods': contact_methods
        })
    return output


def list_escalation_policies(team_id=None):
    """List all escalation policies in account"""

    output = pd_get('/escalation_policies', {
        'limit': 100,
        'team_ids[]': [team_id]
    })
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get(
                '/escalation_policies',
                {'limit': 100, 'offset': offset, 'team_ids[]': [team_id]}
            )
            output['escalation_policies'] = (
                output['escalation_policies'] + r['escalation_policies']
            )
            offset += 100
    return output


def parse_ep_info(escalation_policies):
    """Parse relevant escalation policy info for reporting"""

    output = []
    for ep in escalation_policies:
        rules = []
        for rule in ep['escalation_rules']:
            targets = []
            for target in rule['targets']:
                if target['type'] in ['user', 'user_reference']:
                    target_type = 'user'
                else:
                    target_type = 'schedule'
                targets.append({
                    'id': target['id'],
                    'type': target_type,
                    'name': target['summary']
                })
            rules.append({
                'escalation_delay': rule['escalation_delay_in_minutes'],
                'id': rule['id'],
                'targets': targets
            })
        output.append({
            'name': ep['name'],
            'rules': rules
        })
    return output


def list_schedules(team_id=None):
    """List all schedules in account"""

    output = pd_get('/schedules', {
        'limit': 100,
        'team_ids[]': [team_id]
    })
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/schedules', {
                'limit': 100,
                'offset': offset,
                'team_ids[]': [team_id]
            })
            output['schedules'] = output['schedules'] + r['schedules']
            offset += 100
    return output


def list_schedule_oncalls(schedule_id):
    """List the current on-calls for a schedule"""

    output = pd_get('/oncalls', {
        'since': datetime.now().isoformat(),
        'until': (datetime.now() + timedelta(seconds=1)).isoformat(),
        'schedule_ids[]': [schedule_id],
        'limit': 100
    })
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/oncalls', {
                'since': datetime.now().isoformat(),
                'until': (datetime.now() + timedelta(seconds=1)).isoformat(),
                'schedule_ids[]': [schedule_id],
                'limit': 100,
                'offset': offset
            })
            output['oncalls'] = output['oncalls'] + r['oncalls']
            offset += 100
    return output


def parse_schedule_info(schedules):
    """Parse relevant schedule info for reporting"""

    output = []
    for schedule in schedules:
        output.append({
            'name': schedule['name'],
            'id': schedule['id'],
            'description': schedule['description'],
            'time_zone': schedule['time_zone'],
            'oncalls': parse_oncall_info(
                list_schedule_oncalls(schedule['id'])['oncalls']
            )
        })
    return output


def parse_oncall_info(oncalls):
    """Parse relevant on-call info for reporting"""

    output = []
    for oncall in oncalls:
        output.append({
            'user_name': oncall['user']['summary'],
            'user_id': oncall['user']['id'],
            'escalation_level': oncall['escalation_level'],
            'start': oncall['start'],
            'end': oncall['end']
        })
    return output


def list_teams():
    """List all teams in account"""

    output = pd_get('/teams', {'limit': 100})
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/teams', {'limit': 100, 'offset': offset})
            output['teams'] = output['teams'] + r['teams']
            offset += 100
    return output


def parse_team_info(teams):
    """Parse relevant team info for reporting"""

    output = []
    for i, team in enumerate(teams):
        output.append({
            'name': team['name'],
            'id': team['id'],
            'users': [],
            'schedules': [],
            'escalation_policies': [],
            'services': []
        })
        for user in list_users(team['id'])['users']:
            output[i]['users'].append({
                'name': user['name'],
                'id': user['id']
            })
        for schedule in list_schedules(team['id'])['schedules']:
            output[i]['schedules'].append({
                'name': schedule['name'],
                'id': schedule['id']
            })
        for ep in list_escalation_policies(team['id'])['escalation_policies']:
            output[i]['escalation_policies'].append({
                'name': ep['name'],
                'id': ep['id']
            })
        for service in list_team_services(team['id'])['services']:
            output[i]['services'].append({
                'name': service['name'],
                'id': service['id']
            })
    return output


def list_team_services(team_id):
    """List all services on a team"""

    output = pd_get('/services', {'limit': 100, 'team_ids[]': [team_id]})
    if output['more']:
        offset = 100
        r = {'more': True}
        while r['more']:
            r = pd_get('/services', {
                'limit': 100,
                'offset': offset,
                'team_ids[]': [team_id]
            })
            output['services'] = output['services'] + r['services']
            offset += 100
    return output

if __name__ == '__main__':
    print json.dumps(parse_ep_info(list_escalation_policies()['escalation_policies']))
