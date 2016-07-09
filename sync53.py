#!/usr/bin/env python3

import os.path
import time

import boto.route53
import click
import configparser
import requests

#IP_URLS = ['http://icanhazip.com', 'http://wtfismyip.com/text']
IP_URL = 'http://icanhazip.com'
AWS_CONFIG = '~/.aws/credentials'

def get_my_ip():
    return requests.get(IP_URL).text.strip()

def get_aws_credentials():
    parser = configparser.ConfigParser()
    success = parser.read(os.path.expanduser(AWS_CONFIG))
    if success:
        try:
            return (parser.get('default', 'aws_access_key_id'),
                    parser.get('default', 'aws_secret_access_key'))
        except configparser.NoOptionError:
            print('Unable to find credentials.')
            sys.exit(1)
    else:
        raise IOError('Unable to read AWS credentials')


def set_my_ip(domain, hostname, ip):
    (key_id, secret) = get_aws_credentials()
    route53 = boto.route53.connection.Route53Connection(aws_access_key_id=key_id,
                                                        aws_secret_access_key=secret)
    if hostname:
        fqdn = '.'.join([hostname, domain])
    else:
        fqdn = domain
    zone = route53.get_zone(domain)
    status = zone.update_a(fqdn, ip)
    print(status.status, sep='', end='', flush=True)
    while True:
        status.update()
        if status.status == 'PENDING':
            print('.', sep='', end='', flush=True)
            time.sleep(2.0)
        else:
            print(status.status)
            break


@click.command()
@click.option('-d', '--domain', required=True,
              help='Top level domain managed in Route53')
@click.option('-H', '--hostname', required=False,
              help='Optional hostname to set the DNS A record on, otherwise set A record on the top level domain.')
def main(domain, hostname):
    """
    Find your public facing IP address, and update the DNS information that
    is stored on AWS's Route53 DNS servers.
    """
    ip = get_my_ip()
    print('my ip = %s' % ip)
    set_my_ip(domain, hostname, ip)

if __name__ == '__main__':
    main()
