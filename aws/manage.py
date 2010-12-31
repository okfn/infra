#!/usr/bin/env python
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
import uuid
import time
import datetime
import json
from pprint import pprint

import boto
import boto.ec2

def get_regions():
    regions = dict([ (x.name,x) for x in
        boto.ec2.regions() ])
    return regions


class Manager(object):
    # Alestic Debian Lenny images (see http://alestic.com/)
    # unfortunately images have different names on different instances ..
    amis = {
        'eu-west-1':  {
            'debian-lenny': 'ami-b8446fcc',
            'debian-lenny-64': 'ami-80446ff4',
            'debian-squeeze': 'ami-8c446ff8',
            'debian-squeeze-64': 'ami-745b7000',
            'ubuntu-lucid-32-ebs': 'ami-38bf954c',
            'ubuntu-lucid-32': 'ami-fabe948e',
            'ubuntu-lucid-64-ebs': 'ami-f6340182',
            'ubuntu-lucid-64': 'ami-1e34016a',
            'ubuntu-maverick-64-ebs': 'ami-405c6934',
            },
        'us-east-1':  {
            'debian-lenny': 'ami-dcf615b5',
            'debian-lenny-64': 'ami-f0f61599',
            'debian-squeeze': 'ami-dcf615b5',
            'debian-squeeze-64': 'ami-fcf61595',
            'ubuntu-karmic': 'ami-bb709dd2',
            },
        'us-west-1': {
            'debian-lenny': 'ami-b33a6bf6'
            }
        }
    # yes, i know they are inconsistent!
    key_pairs = {
        'eu-west-1': 'okfn-eu1-kp',
        'us-east-1': 'okfn-kp',
        'us-west-1': 'okfn-kp-us-west-1'
        }
    default_ami_type = 'ubuntu-lucid-32'
    region_names = [ 'us-east-1', 'us-west-1', 'eu-west-1' ]

    def __init__(self, region=None, server_info_path='../servers.js'):
        '''
        @param region: AWS region identifier (us-east-1, us-west-1, eu-west-1)
        '''
        # simple default self.connection
        # self.conn = boto.self.connect_ec2(AKEY, SKEY)
        self.conn = None
        self.regions = get_regions()
        self.region = region
        self.server_info_path = server_info_path
        self.server_info = json.load(open(os.path.abspath(server_info_path)))

    def _connect(self):
        region = self.regions[self._region]
        self.conn = region.connect()
        
    def _get_region(self):
        return self._region
        
    def _set_region(self, value):
        self._region = value
        if self._region is not None:
            self._connect()

    region = property(_get_region, _set_region)

    def _save_server_info(self):
        with open(self.server_info_path, 'w') as fo:
            json.dump(self.server_info, fo, indent=2, sort_keys=True)

    def _get_server_by_instance_id(self, instance_id):
        for k,v in self.server_info.items():
            if v.get('aws_id', None) == instance_id:
                return k
    
    def _timestamp(self):
        return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    
    def placement(self):
        '''The placement of an existing instance in this region (or None if no
        instance).
        '''
        reservation = self.conn.get_all_instances()
        existing = reservation[0].instances[0] if reservation else None
        placement = getattr(existing, 'placement', None)
        return placement

    def create_instance(self, ami=None, instance_type='m1.small', okfn_id=None, **kwargs):
        '''Create a standard EC2 instance automatically.
        
            # e.g. for ebs-backed instance with ubunut lucid in eu west with
            # okfn-id euX
            create_instance --region eu-west-1 ubuntu-lucid-32-ebs t1.micro euX

        Automatically: a) assign security groups b) put in same availability
        zone as other instances in this region. Post-boot you may want to:
            1. allocate an ip (allocate_ip)
            2. relocate var on /mnt (which is the large volume) (see
                fabfile.py)
            3. install standard software

        @param ami: name of ami to use (see self.amis for options). If None use
            self.default_ami_type.
        @param **kwargs: passed directly into boto `run_instances`
        @return: tuple of boto instance object representing created instance
            and an dict with info about that instance (as for servers.js).
        '''
        # create a dedicated secgroup for this machine
        secname = 'instance-%s' % uuid.uuid4()
        oursecgroup = self.conn.create_security_group(secname, secname)
        secgroups = [ 'default', 'www-only', 'ssh-only', 'munin-only', secname ]

        ourami = ami if ami else self.amis[self.region][self.default_ami_type]
        if not ourami.startswith('ami-'): # it a dist name e.g. debian-squeeze
            ourami = self.amis[self.region][ourami]
        ourkwargs = {
            'placement': self.placement(),
            'instance_type': instance_type,
            'key_name': self.key_pairs[self.region],
            'security_groups': secgroups
        }
        ourkwargs.update(kwargs)

        reservation = self.conn.run_instances(ourami, **ourkwargs)
        instance = reservation.instances[0]
        while instance.state == 'pending':
            time.sleep(10)
            print('Waiting for instance to go active')
            instance.update()
        print('Instance active')

        infodict = dict(ourkwargs)
        del infodict['key_name']
        infodict.update({
            "owner": "okfn",
            "os": ami,
            "created": self._timestamp(),
            "aws_id": instance.id,
            "notes": None,
            "location": self.region,
            "provider": "aws", 
            "type": "ec2", 
            "aws_public_dns_name": instance.public_dns_name,
            "aws_private_dns_name": instance.private_dns_name,
            "volumes": {}
        })
        if okfn_id:
            self.server_info[okfn_id] = infodict
            self._save_server_info()
        return instance, infodict
    
    def allocate_ip(self, instance_id):
        '''Allocate ip address to instance_id.'''
        print('Allocating IP')
        ipaddr = self.conn.allocate_address()
        self.conn.associate_address(instance_id, ipaddr.public_ip)

    def associate_address(self, instance_id, ipaddr):
        '''Associate address.'''
        self.conn.associate_address(instance_id, ipaddr)

    def create_security_groups(self):
        '''Create standard security groups (web, ssh).
        '''
        # TODO: check they do not already exist
        # secgroups = self.conn.get_all_security_groups()
        # secnames = [s.name for s in secgroups]
        web = self.conn.create_security_group('www-only', 'www-only')
        web.authorize('tcp', 80, 80, '0.0.0.0/0')
        web.authorize('tcp', 443, 443, '0.0.0.0/0')
        ssh = self.conn.create_security_group('ssh-only', 'ssh-only')
        ssh.authorize('tcp', 22, 22, '0.0.0.0/0')
        munin = self.conn.create_security_group('munin-only', 'munin-only')
        munin.authorize('tcp', 4949, 4949, '79.125.8.34/32')

    def update_security_group(self, name, port, protocol='tcp',
            ip='0.0.0.0/0'):
        '''Add permission to security group `name` for port `port`.
        '''
        secgroup = self.conn.get_security_group
        self.conn.authorize_security_group(name, ip_protocol=protocol,
                from_port=port, to_port=to_port, cidr_ip=ip)

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
    def create_ebs(self, instance, size=50, attach_point='/dev/sdp',
            description='backup'):
        '''Create ebs volume attached to `instance` of `size` gb and attach to
        instance at `attach_point`.
 
        NB: instance can be a string in which case assumed to be an instance.id
        :param instance: instance can be a string in which case assumed to be an instance.id
        :param size: size in GB (defaults to 50)
        :param attach_point: mount point (defaults to /dev/sdp)
        '''
        if isinstance(instance, basestring):
            instance = self.conn.get_all_instances([instance])[0].instances[0]
        v = self.conn.create_volume(size, instance.placement)
        v.attach(instance.id, attach_point)
        print 'Volume attached. You may now wish to format it.'
        serverid = self._get_server_by_instance_id(instance.id)
        vols = self.server_info[serverid]['volumes'][v.id] = {
            'device': v.attach_data.device,
            'description': description
            }
        print 'Run: mke2fs -m0 -j %s' % attach_point
        return v
    
    def snapshot_backup_volumes(self):
        '''Snapshot all backup volumes in this cluster (backup vol identified
        by being attached to /dev/sdp)'''
        ebs_volumes = self.conn.get_all_volumes()
        for v in ebs_volumes:
            if v.attach_data.device == '/dev/sdp':
                instanceid = v.attach_data.instance_id
                okfn_id = self._get_server_by_instance_id(instanceid)
                desc = '%s::backup::%s' % (okfn_id, self._timestamp())
                print('Creating snapshot: %s' % desc)
                v.create_snapshot(desc)

    def info(self):
        '''Get info dict about this region's instances, security groups etc (if
        using from the cli recommend `print_info`).
        '''
        res = {
            'region': self.conn.region,
            'security-groups': self.conn.get_all_security_groups(),
            'addresses': self.conn.get_all_addresses(),
            }
        res['instances'] = self.conn.get_all_instances()
        return res

    def print_info(self):
        '''Print results of info() to stdout'''
        print('Available Regions', get_regions())
        res = self.info()
        print('Current Region', res['region'])
        print('Addresses', res['addresses'])
        for instset in res['instances']:
            for inst in instset.instances:
                # TODO: describe an instance better
                print inst, inst.state, inst.dns_name, inst.placement
        for addr in res['addresses']:
            print(addr.public_ip, addr.instance_id)
        return ''

    def image_info(self, image_id):
        '''Print information about image specified by image_id'''
        m = Manager()
        image = m.conn.get_image(image_id)
        print image


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
    _methods = _object_methods(Manager)
    usage = '''%prog {action} [args]

    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__ if m.__doc__ else '') for (name,m)
        in _methods.items() ])
    parser = optparse.OptionParser(usage)
    parser.add_option('-r', '--region', dest='region',
            help='Region to connect to (default: %s)' % ','.join(Manager.region_names),
            default=Manager.region_names[0])
    parser.add_option('--servers', dest='servers',
            help='Path to server info json file (default: %s)' % ('../servers.js'),
            default='../servers.js')
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)
    manager = Manager(options.region, options.servers)
    method = args[0]
    out = getattr(manager, method)(*args[1:])
    if out:
        print out

