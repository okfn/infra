import EventRegistration

import StringIO

class Test1:

    def test_save_data(self):
        fileobj = StringIO.StringIO()
        name = 'Anna Karenina'
        email = 'tolstoy@tolstoy.com'
        entry = '%s <%s>\n' % (name, email)
        EventRegistration.save_data(fileobj, name, email)
        fileobj.seek(0)
        out = fileobj.read()
        assert out == entry
        fileobj.seek(0)
        numregs = EventRegistration.count_registrations(fileobj)
        assert numregs == 1
    
    def test_make_form(self):
        values = {
            'pageurl' : 'TestMacro',
            'msg'      : '',
            'name' : '',
            'email' : '',
            'email2' : '',
            'registered_total' : 0,
            }
        out = EventRegistration.make_form(values)
        assert '<form' in out
        assert values['pageurl'] in out

    def test_check_data(self):
        fail_set = [
                ('', '', ''),
                ('', 'xyz', ''),
                ('', 'xyz@xyz.com', ''),
                ('xyz', 'xyz@xyz.com', ''),
                ]
        success_set = [
                ('Anna K', 'anna@karenina.org', 'anna@karenina.org'),
                ]
        def check_fail(values):
            status, msg = EventRegistration.check_data(values[0], values[1],
                    values[2])
            assert not status

        for values in fail_set:
            yield check_fail, values

        def check_success(values):
            status, msg = EventRegistration.check_data(values[0], values[1],
                    values[2])
            assert status

        for values in success_set:
            yield check_success, values
        
# import twill
class TestWebInterface:
    pass
