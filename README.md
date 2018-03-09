# SSL Termination FQDN

This charm installs a subordinate for the [SSL Termination Proxy](https://github.com/tengu-team/layer-ssl-termination-proxy).
It requests ssl-termination for a webservice.

## Configs

It has 3 config values:

- **`fqdns`** is a space separated list of domain names on which the webservice should be accessable. Note: make sure to point the DNS records of these domain names to the ssl-termination-proxy. *Example: `"example.com www.example.com"`.*
- **`credentials`** is a space-separated pair of username and password for basic authentication.
- **`contact-email`** is the contact email address for lets encrypt. This email address will receive notifications when the certificate expires. Note that the ssl-termination-proxy automatically renews certificates after 2 months so you will only get an email when something is broken.

## How to use

See the `ssl-termination-proxy` charm for more info on how to use this.

```bash
# Deploy your http webservice.
juju deploy jenkins
# Deploy your ssl-termination-fqdn
juju deploy cs:~tengu-team/ssl-termination-fqdn fqdn-jenkins
# Configure the client
juju config fqdn-jenkins fqdns="example.com www.example.com"
juju config fqdn-jenkins basic_auth="username password"
# Connect the webservice with the ssl client
juju add-relation jenkins fqdn-jenkins
# Connect the ssl-client with the proxy.
juju add-relation fqdn-jenkins:ssltermination ssl-termination-proxy:ssltermination
# Now you can surf to https://example.com and you wil reach the webservice.
```

## Authors

This software was created in the [IDLab research group](https://www.ugent.be/ea/idlab) of [Ghent University](https://www.ugent.be) in Belgium. This software is used in [Tengu](https://tengu.io), a project that aims to make experimenting with data frameworks and tools as easy as possible.

- Sander Borny <sander.borny@ugent.be>
- Merlijn Sebrechts <merlijn.sebrechts@gmail.com>
- Crawler icon made by [Vectors Market](https://www.flaticon.com/authors/vectors-market) from [www.flaticon.com](www.flaticon.com) licensed as [Creative Commons BY 3.0](http://creativecommons.org/licenses/by/3.0/)
