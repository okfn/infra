"""Event Registration macro for moinmoin.

Macro requires one argument: the path to the file where registration details
are stored.

Registration details are stored as 'name <email>' in the file.

@author: Rufus Pollock (Open Knowledge Foundation)
@copyright: (c) 2006, Open Knowledge Foundation
@license: MIT license <www.opensource.org/licenses/mit-license.php> 

TODO:
=====

1. Email confirmation

2. multiple attendees per registrant

3. Display list of attendees

4. store more information than just name and email

5. (Refactoring) Automate form generation and value extraction

6. css styling of the form

7. object-orient the storage mechanism e.g. something like

class RegistrationStore(object):
    pass

class RegistrationStoreFile(RegistrationStore):

    def __init__(self, fileobj):
        self.fileobj = fileobj
"""


# VERY WEIRD behaviour (that cost me 2 hours)
# if you have Dependencies = [] macro.form is NOT set
# Dependencies = []

import StringIO
DEBUG = False

def execute(macro, args):
    # return macro.formatter.text("I got these args from a macro %s: %s" % (str(macro), args))
    filepath = args.strip()

    pageurl = macro.formatter.page.url(macro.request)

    name = macro.form.get('name', [''])[0]
    email = macro.form.get('email', [''])[0]
    email2 = macro.form.get('email2', [''])[0]
    form_submitted = macro.form.get('form_submitted', ['n'])[0]

    # processing order
    # if no_submit: display the standard form
    # else:
    #   if check_data: display standard form with msg

    msg = ''
    if form_submitted == 'y': 
        data_ok, msg = check_data(name, email, email2)
        if data_ok:
            try:
                fileobj = file(filepath, 'a')
                save_data(fileobj, name, email)
                msg = 'Registration successful'
            except:
                msg = 'Unable to save registration. Please contact the system administrator'
    template_values = {
            'pageurl' : pageurl,
            'msg'      : msg,
            'name'     : name,
            'email'    : email,
            'email2'   : email2
            }
    result = make_form(template_values)
    if DEBUG:
        debug_msg = str(macro.form)
        result += 'Debug is: %s' % debug_msg
    return result 

def check_data(name, email, email2):
    def is_valid_email(address):
        return email != '' and '@' in email
    
    if not is_valid_email(email):
        msg = 'Please supply a valid email address'
        return False, msg
    if email2 != email:
        msg = 'Email addresses did not match'
        return False, msg
    if name == '':
        msg = 'Please supply a name.'
        return False, msg
    return True, ''

def save_data(fileobj, name, email):
    entry = '%s <%s>\n' % (name, email)
    fileobj.write(entry)

def make_form(template_values):
    def text_form_field(label, name, value=''):
        res = '<label for="%s">%s</label>' % (name, label)
        # res += '<br />\n'
        res += ' <input type="text" id="%s" name="%s" value="%s" />' % (name,
            name, value)
        res += '<br />'
        return res
        
    template = '''
<span style="color: red; font-weight: bold;">%(msg)s</span>
<form name="add_attendee" action="%(pageurl)s#register" METHOD="POST">
'''
    template += text_form_field('Name:', 'name', template_values['name'])
    template += text_form_field('Email:', 'email', template_values['email'])
    template += text_form_field('Repeat Email:', 'email2',
        template_values['email2'])
    template += '''
    <input type="hidden" name="form_submitted" value="y" />
    <input type="submit" name="button_save" value="Register" />
</form>
        '''
    html = template % template_values 
    return html

def make_form_test(macro):
    template = '''
<form action="TestMacro#add" name="comment" METHOD="POST" >
<textarea name="comtext" rows="4" cols="60" style="font-size: 9pt;" 
Add your comment</textarea>
<input type="submit" name="button_save" value="Save">
</form>
'''
    return template

