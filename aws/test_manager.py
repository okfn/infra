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
        # TODO: could test for eu-west-1 too
        manager = Manager('us-west-1')
        instance = manager.create_instance()
        assert instance.id
        instance.stop()

