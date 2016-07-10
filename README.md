sync53
======

OVERVIEW
--------

Run sync53 to figure out your public-facing IP address, and
update the DNS record for your domain name or a hostname to
that IP address.

CONFIGURATION
-------------

First, make sure you have a user configured on AWS with the `AmazonRoute53DomainFullAccess` and `AmazonRoute53FullAccess` policies attached. (You might need only one of those two, but I haven't taken the time to figure out which one yet.)

You'll then need to create a .ini style config file in your home directory with that user's Key and Secret information stored. The full path should be ~/.aws/credentials and should contain a `[default]` section `aws_access_key_id` and `aws_secret_access_key` properties with your Access Key and Secret.

For example:

    [default]
    aws_access_key_id = A1B2C3D4E5F6G7H8I9J0
    aws_secret_access_key = ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789

RUNNING
-------

All you need to do now is run sync53 something like this:

`sync53 --domain example.com`

to set the IP address on the top level `example.com` DNS record.

or

`sync53 --hostname www --domain example.com`

to set the IP address on the `www.example.com` DNS record.

CAVEATS
-------

This currently only set IPv4 `A` records.

FUTURE
------

+ IPv6 `AAAA` records
+ Check multiple sources for what your IP address is to avoid any (unlikely) takeover attempts of your traffic.
+ Should really check what Amazon thinks your IP address is before setting it to the same value.
