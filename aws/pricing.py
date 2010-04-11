# large is just 4x everything ...
cph = { 'eu': 0.095, 'us': 0.085 }
cph_res = { 'eu': 0.04, 'us': 0.03 }
res_cost = 227.50

def break_even():
    # calculate point at which reserved instance is better
    cph = 0.085
    res_cph = 0.03
    res_cost = 227.50
    bw_cost = 0.17 # per gb
    bw_usage = 90 # per month

    # num_hours * cph = res_cost + num_hours * res_cph
    num_hours = res_cost / (cph - res_cph)
    print('Number of days until reservation is better: %s' % (num_hours /
        24.0))

    print('annual cost of reserved: %s' % (res_cph*24*365 + res_cost +
        12*90*0.17))

def eu_us_diff():
    diff = 30 * 24 * (cph['eu'] - cph['us'])
    print('Price diff b/w eu and us per month: %s' % diff)
    print('Price diff b/w eu and us per year: %s' % (12*diff))

def cost_per_month(size='small', region='us'):
    cost = cph[region] * 24 * 30
    cost_res = res_cost / 12.0 + cph_res[region] * 24 * 30
    if size == 'large':
        cost_res = 4 * cost_res
        cost = 4 * cost
    print('Size: %s, Region: %s' % (size, region))
    print('Cost per month (1 year reserved): %s' % cost_res)
    print('Cost per month (no reservation): %s' % cost)


import os
import sys
import optparse
import inspect
def _module_functions(functions):
    local_functions = dict(functions)
    for k,v in local_functions.items():
        if not inspect.isfunction(v) or k.startswith('_'):
            del local_functions[k]
    return local_functions

def _main(functions_or_object):
    isobject = inspect.isclass(functions_or_object)
    if isobject:
        _methods = _object_methods(functions_or_object)
    else:
        _methods = _module_functions(functions_or_object)

    usage = '''%prog {action}

    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__.split('\n')[0] if m.__doc__ else '') for (name,m)
        in _methods.items() ])
    parser = optparse.OptionParser(usage)
    # Optional: for a config file
    # parser.add_option('-c', '--config', dest='config',
    #         help='Config file to use.')
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)

    method = args[0]
    if isobject:
        getattr(functions_or_object, method)()
    else:
        _methods[method](*args[1:])


if __name__ == '__main__':
    _main(locals())
