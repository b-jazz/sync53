#!/usr/bin/env python3

import logging
import os.path
import socket
import time

import boto.route53
import click
import configparser
import requests


IP_URLS = ['http://icanhazip.com', 'http://wtfismyip.com/text', 'http://ip.42.pl/raw']
IP_URL = 'http://icanhazip.com'
AWS_CONFIG = '~/.aws/credentials'


logging.basicConfig()
log = logging.getLogger(__name__)


def get_ip_from_url(url):
    try:
        response = requests.get(IP_URL)
    except Exception as ex:
        raise LookupError('Exception fetching from {0}: {1}'.format(url, ex))
    else:
        if response.ok:
            return response.text.strip()
        else:
            raise LookupError('Unable to fetch IP from %s.' % url)


def get_my_ip():
    success_count = 0
    unique_ips = set()
    for url in IP_URLS:
        try:
            ip = get_ip_from_url(url)
        except LookupError as ex:
            print('{0}'.format(ex))
        else:
            success_count += 1
            log.debug('Found IP %s from %s', ip, url)
            unique_ips.add(ip)

    if len(unique_ips) == 1:
        return unique_ips.pop()
    else:
        print('ERROR: Multiple IPs found: {0}'.format(unique_ips))


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
              help=('Optional hostname to set the DNS A record on, '
                    'otherwise set A record on the top level domain.'))
@click.option('--debug', required=False, is_flag=True,
              help='Turn on more verbose debugging information')
def main(domain, hostname, debug):
    """
    Find your public facing IP address, and update the DNS information that
    is stored on AWS's Route53 DNS servers.
    """
    if debug:
        log.setLevel(logging.DEBUG)

    ip = get_my_ip()
    print('my ip = %s' % ip)

    try:
        ip_via_dns = socket.gethostbyname('.'.join([hostname, domain]))
    except socket.gaierror:
        ip_via_dns = ''

    if ip != ip_via_dns:
        log.debug('IP different between DNS (%s) and reality (%s).', ip_via_dns, ip)
        set_my_ip(domain, hostname, ip)
    else:
        log.debug('No need to update Route53. IPs are the same.')


if __name__ == '__main__':
    main()
