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
from charms.reactive import (
    when,
    when_not,
    set_flag,
    clear_flag,
    when_any,
    is_flag_set,
)
from charms.reactive.relations import endpoint_from_flag


config = config()


########################################################################
# Install
########################################################################

@when('endpoint.ssl-termination.available')
@when_not('website.available',
          'endpoint.tcp.joined')
def missing_service_relation():
    clear_flag('client.cert-created')
    status_set('blocked', 'Waiting for http/tcp relation')


@when_any('website.available',
          'endpoint.tcp.joined')
@when_not('endpoint.ssl-termination.available')
def missing_ssl_termination_relation():
    status_set('blocked', 'Waiting for ssl-termination-proxy relation')


@when_any('config.changed.fqdns',
          'config.changed.credentials')
def fqdns_changed():
    clear_flag('client.cert-requested')
    clear_flag('client.cert-created')


########################################################################
# Configure certificate
########################################################################

@when('endpoint.ssl-termination.available')
@when_any('website.available',
          'endpoint.tcp.joined')
@when_not('client.cert-requested')
def create_cert_request():
    if not config.get('fqdns'):
        status_set('blocked', 'Waiting for fqdns config')
        return
    
    ssl_termination = endpoint_from_flag('endpoint.ssl-termination.available')
    upstreams = []
    tcps = []

    if is_flag_set('website.available'):
        website = endpoint_from_flag('website.available')

        services = website.services()
        if not services:
            return        
        for service in services:
            upstreams.extend(service['hosts'])

    if is_flag_set('endpoint.tcp.joined'):
        tcp = endpoint_from_flag('endpoint.tcp.joined')
        tcp_svcs = tcp.tcp_services()
        tcps = transform_tcp_services(tcp_svcs)
        if not tcps:
            return

    ssl_termination.send_cert_info({
        'fqdn': config.get('fqdns').rstrip().split(),
        'contact-email': config.get('contact-email', ''),
        'credentials': config.get('credentials', ''),
        'upstreams': upstreams,
        'tcp': tcps,
    })
    status_set('waiting', 'Waiting for proxy to register certificate')
    set_flag('client.cert-requested')


@when('endpoint.ssl-termination.available',
      'client.cert-requested')
@when_any('website.available',
          'endpoint.tcp.joined',
          'endpoint.ssl-termination.update')
@when_not('client.cert-created')
def check_cert_created():
    ssl_termination = endpoint_from_flag('endpoint.ssl-termination.available')
    status = ssl_termination.get_status()

    # Only one fqdn will be returned for shared certs.
    # If any fqdn match, the cert has been created.
    match_fqdn = config.get('fqdns').rstrip().split()
    for unit_status in status:
        if not unit_status['status']:
            continue
        for fqdn in unit_status['status']:
            if fqdn in match_fqdn:
                status_set('active', 'Ready')
                set_flag('client.cert-created')
    if is_flag_set('endpoint.ssl-termination.update'):
        clear_flag('endpoint.ssl-termination.update')


########################################################################
# Unconfigure certificate
########################################################################

@when('endpoint.ssl-termination.available',
      'client.cert-requested')
@when_not('website.available',
          'endpoint.tcp.joined')
def website_removed():
    endpoint = endpoint_from_flag('endpoint.ssl-termination.available')
    endpoint.send_cert_info({})
    clear_flag('client.cert-requested')
    clear_flag('client.cert-created')


########################################################################
# Helper methods
########################################################################

def transform_tcp_services(tcp_services):
    transform = []
    for service in tcp_services:
        host_ips = []
        port = None
        for host_port in service['hosts']:
            host_ips.append(host_port['host'])
            if port and port != host_port['port']:
                status_set('blocked', 'Received multiple hosts from a single service with different ports.')
                break
            port = host_port['port']
        transform.append({
            'hosts': host_ips,
            'port': port,
        })
    return transform

