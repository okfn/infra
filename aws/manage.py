'''Automate standard tasks with AWS (EC2) using boto.

You should specify credentials (access key, secret key) either via ~/.boto or
via environment variables. See http://code.google.com/p/boto/wiki/BotoConfig.

Research
========

Doing stuff with EBS
  * http://www.elastician.com/2009/12/creating-ebs-backed-ami-from-s3-backed.html
  * http://aws-musings.com/how-to-expand-your-ebs-volume/

Post install scripts
  * http://alestic.com/2009/08/runurl
  * http://alestic.com/2009/06/ec2-user-data-scripts

May be useful
  * http://www.elastician.com/2009/12/creating-ebs-backed-ami-from-s3-backed.html

Questions:
=========

1. Why use EBS now EC2 instances can be permanent and size limitations are
much removed (now 160GB on instance)?
  * EBS I/O performance is problematic
    (http://victortrac.com/EC2_Ephemeral_Disks_vs_EBS_Volumes)
  * EBS is additional expense
  * EBS does have nicer snapshotting than instance but is possible
'''
import os

import boto
import boto.ec2

def get_regions():
    regions = dict([ (x.name,x) for x in
        boto.ec2.regions() ])
    return regions

class Manager(object):
    # Alestic Debian Lenny images (see http://alestic.com/)
    # unfortunately images have different names on different instances ..
    ami_debian_euwest = 'ami-b8446fcc'
    ami_debian_useast = 'ami-dcf615b5'

    def __init__(self, region='us-east-1'):
        '''
        @param region: AWS region identifier (us-east-1, us-west-1, eu-west-1)
        '''
        # simple default self.connection
        # self.conn = boto.self.connect_ec2(AKEY, SKEY)
        region = get_regions()[region]
        self.conn = region.connect()

    def create_instance(self):
        '''Create a standard EC2 instance using our default security groups.

        @return: boto instance object representing created instance.
        '''
        secgroups = self.security_groups()
        # use default keypair
        reservation = self.conn.run_instances(
            self.ami_debian_euwest,
            instance_type='m1.small',
            security_groups=secgroups)
        instance = reservation.instances[0]
        while instance.state == 'pending':
            time.sleep(10)
            instance.update()
        # TODO: now do post-boot stuff
        # attach ip
        # install standard software
        # either
        # a) attach EBS instances
        # b) relocate var on /mnt (which is the large volume)
        #    (see aws_fabfile.py)
        return instance

    def create_security_groups(self):
        '''Create standard security groups (web, ssh).
        '''
        web = self.conn.create_security_group('www-only', 'www-only')
        web.authorize('tcp', 80, 80, '0.0.0.0/0')
        web.authorize('tcp', 443, 443, '0.0.0.0/0')
        ssh = self.conn.create_security_group('ssh-only', 'ssh-only')
        ssh.authorize('ssh', 22, 22, '0.0.0.0/0')

    def instance_security_groups(self):
        '''Get security groups to apply to a given instance'''
        existing = self.conn.get_all_security_groups()
        # if not 'SecurityGroup:www-only' not in existing:
            # self.create_security_groups()
        # assume we apply all groups
        # since sec groups cannot be changed once instance created may be worth
        # creating a dedicated group just for this instance
        return existing

    # see here for details on attaching and checking volume is available
    # http://groups.google.com/group/boto-users/browse_thread/thread/c4051181a1b8904d
    def create_ebs(self, instance):
        '''Create a 60GB EBS and attach to instance at /dev/sdh
        '''
        v = self.conn.create_volume(60, instance.placement)
        v.attach(instance.id, '/dev/sdh')

    def info(self):
        '''Get dictionary of info about this region's instances, security
        groups etc.
        '''
        res = {
            'region': self.conn.region,
            'security-groups': self.conn.get_all_security_groups(),
            }
        res['instances'] = self.conn.get_all_instances()
        return res

    def print_info(self):
        '''Print results of info() to stdout'''
        res = self.info()
        print('Regions', get_regions())
        print res
        for inst in res['instances'][0].instances:
            print inst, inst.state, inst.dns_name

    def image_info(self, image_id):
        '''Print information about image specified by image_id'''
        m = Manager()
        image = m.conn.get_image(image_id)
        print image


class TestManager:
    def test_info(self):
        regionstr = 'eu-west-1'
        m = Manager(regionstr)
        out = m.info()
        assert out['region'].name == regionstr


import os
import sys
import optparse
import inspect
def _object_methods(obj):
    methods = inspect.getmembers(obj, inspect.ismethod)
    methods = filter(lambda (name,y): not name.startswith('_'), methods)
    methods = dict(methods)
    return methods

if __name__ == '__main__':
    # image_info(Manager.ami_debian_euwest)
    manager = Manager()
    _methods = _object_methods(manager)
    usage = '''%prog {action} [args]

    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__.split('\n')[0] if m.__doc__ else '') for (name,m)
        in _methods.items() ])
    parser = optparse.OptionParser(usage)
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)
    method = args[0]
    getattr(manager, method)(*args[1:])

