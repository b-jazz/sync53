#!/usr/bin/env python

import configparser
import os.path
import requests
import time

import boto.route53
#import click

IP_URL = 'http://icanhazip.com'
AWS_CONFIG = '~/.aws/credentials'
DOMAIN = 'example.com.'

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

def set_my_ip(hostname, ip):
    (key_id, secret) = get_aws_credentials()
    route53 = boto.route53.connection.Route53Connection(aws_access_key_id=key_id,
                                                        aws_secret_access_key=secret)
    zone_id = route53.get_hosted_zone_by_name(DOMAIN)['GetHostedZoneResponse']['HostedZone']['Id']
    print('zone_id = %s' % zone_id)
    fqdn = '%s.%s' % (hostname, DOMAIN)
    zone = route53.get_zone(DOMAIN)
    status = zone.update_a(fqdn, ip)
    print('Update status: %s' % status.status)
    print('Sleeping 60 seconds...')
    time.sleep(60.0)
    status.update()
    print('Update status: %s' % status.status)


def main():
    ip = get_my_ip()
    print('my ip = %s' % ip)
    set_my_ip('dnssync', ip)

if __name__ == '__main__':
    main()

