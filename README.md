# SSL Termination Client

This charm installs a subordinate for the [SSL Termination Proxy](https://github.com/tengu-team/layer-ssl-termination-proxy).
It contains the specific config options for a webservice: domain names, basic_auth and type of loadbalancing.

# Configs

It has 3 config values:
- fqdns
This is a single space separated list of domain names on which the webservice will be accessable.
Example: `"example.com www.example.com"`
- basic_auth
Multiple user and password combinations can be given. Each user-password combo is separated by double spaces, and each user and password is separated by ` | `. The password itself can contain the `|` character.
Example: `"root | example|1  test | example"`
- loadbalancing
Sets the type of loadbalancing to be used. NGINX supports 3 types, [roundrobin, least-connected and ip-hash](http://nginx.org/en/docs/http/load_balancing.html). In order to use roundrobin, an empty string must be provided (which is the default value), otherwise `least-connected` or `ip-hash`. When an incorrect value is given, the charm will go into a blocked state
# How to use

```bash
# Deploy your http webservice.
juju deploy jenkins
# Deploy your proxy-client
juju deploy cs:~tengu-team/ssl-termination-client ssl-jenkins
# Configure the client
juju config ssl-jenkins fqdns="example.com www.example.com"
juju config ssl jenkins basic_auth="root | example|1  test | example"
# Connect the webservice with the ssl client
juju add-relation jenkins ssl-jenkins
# Connect the ssl-client with the proxy.
juju add-relation ssl-jenkins:ssltermination ssl-termination-proxy:ssltermination
# Now you can surf to https://example.com and you wil reach the webservice.
```

## Authors

This software was created in the [IBCN research group](https://www.ibcn.intec.ugent.be/) of [Ghent University](https://www.ugent.be/en) in Belgium. This software is used in [Tengu](https://tengu.io), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@ugent.be>
 - Merlijn Sebrechts <merlijn.sebrechts@gmail.com>
 - Mathijs Moerman <mathijs.moerman@tengu.io>
