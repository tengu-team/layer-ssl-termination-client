#!/usr/bin/env python3
# Copyright (C) 2017  Qrama, developed by Tengu-team
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os

from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import status_set, config

from charms.reactive import when, when_not, set_state, remove_state


db = unitdata.kv()


@when('ssltermination.connected')
@when_not('http.available')
def initial(ssltermination):
    status_set('blocked', 'Waiting for relation with http-service')


@when('http.available')
@when_not('client.initial_http')
def setup(http):
    service = os.environ['JUJU_REMOTE_UNIT'].split('/')[0]
    db.set('service_name', service)
    set_state('client.initial')
    private_ips = ['{}:{}'.format(h['hostname'], h['port']) for h in http.services()[0]['hosts']]
    db.set('private_ips', private_ips)
    set_state('client.initial_http')


@when('http.available', 'client.configured')
def update(http):
    private_ips = ['{}:{}'.format(h['hostname'], h['port']) for h in http.services()[0]['hosts']]
    if private_ips != db.get('private_ips'):
        db.set('private_ips', private_ips)
        remove_state('client.configured')


@when('ssltermination.connected', 'client.initial_http')
@when_not('client.configured')
def request(ssltermination):
    status_set('active', 'Configuring domainnames and NGINX configs')
    ssltermination.request_proxy(
        db.get('service_name'),
        db.get('fqdns'),
        db.get('private_ips'),
        db.get('basic_auth'),
        db.get('loadbalancing')
    )
    set_state('client.configured')


@when('ssltermination.available')
def done(ssltermination):
    status_set('active', 'SSL-proxy config: Done')


@when('config.changed')
def changed_config():
    fqdns = config()['fqdns'].split(' ')
    try:
        basic_auth = [
            {'user': u.split(' | ', 1)[0], 'password': u.split('  ', 1)[1]}
            for u in config()['basic_auth'].split(' | ')
        ]
    except IndexError:
        basic_auth = []
    lb = config()['loadbalancing']
    loadbalancing = lb if lb in ['least-connected', 'ip-hash'] else ''
    db.set('fqdns', fqdns)
    db.set('basic_auth', basic_auth)
    db.set('loadbalancing', loadbalancing)
    status_set('maintenance', 'Reconfiguring')
    remove_state('client.configured')
