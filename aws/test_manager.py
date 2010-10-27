'''Test for AWS Manager.

TODO: we should really create our own account for testing!
'''
from manage import Manager

class TestManager:
    def test_01_info(self):
        regionstr = 'eu-west-1'
        m = Manager(regionstr)
        out = m.info()
        assert out['region'].name == regionstr

    def test_02_placement(self):
        m = Manager('us-east-1')
        assert m.placement() == 'us-east-1d', m.placement()

    # this costs money to run :)
    def test_03_create(self):
        print('WARNING: if test fails ensure created instance termination to avoid running up charges')
        # TODO: could test for eu-west-1 too
        manager = Manager('us-west-1')
        instance, infodict = manager.create_instance()
        assert infodict['aws_id'] == instance.id
        assert infodict['aws_public_dns_name']
        instance.stop()

    def test_04_server_info(self):
        regionstr = 'eu-west-1'
        m = Manager(regionstr)
        assert 'eu3' in m.server_info.keys()
        aws_id = 'i-2275d655'
        assert m._get_server_by_instance_id(aws_id) == 'eu3'

