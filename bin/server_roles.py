import os, collections, pprint

try:
    import json
except:
    import simplejson as json

SERVERS_JS = os.path.join(os.path.dirname(__file__), '..', 'servers.js')

PROPERTY_BLACKLIST = [
    'created',
    'cost per month',
]

def get_roles():
    """ parse server.js and return fabric role definitions 
    """
    servers = collections.defaultdict(list)    
    for hostname, props in json.load(file(SERVERS_JS)).items():
        
        # fab requires a FQDN 
        hostname += '.okfn.org'
        
        servers['all'].append(hostname)

        for name, value in props.items():
            if value and name not in PROPERTY_BLACKLIST: 
                servers[value].append(hostname)
            
        
        # servers[props.get('provider')].append(hostname)
    return dict(servers)
        
if __name__ == '__main__':
    print pprint.pprint(get_roles())