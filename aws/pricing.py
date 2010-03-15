cph = { 'eu': 0.095, 'us': 0.085 }
cph_res = { 'eu': 0.04, 'us': 0.03 }

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

break_even()
eu_us_diff()

