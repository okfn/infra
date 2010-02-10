from manage import Manager

class TestManager:
    def test_info(self):
        regionstr = 'eu-west-1'
        m = Manager(regionstr)
        out = m.info()
        assert out['region'].name == regionstr

    def test_create(self):
        manager = Manager('eu-west-1')
        instance = manager.create_instance()
        assert instance.id
        instance.terminate()

