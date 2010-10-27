import os, collections, pprint

try:
    import json
except:
    import simplejson as json

SERVERS_JS = os.path.join(os.path.dirname(__file__), '..', 'servers.js')

def get_roles():
    """ parse server.js and return fabric role definitions 
    """
    servers = collections.defaultdict(list)    
    for hostname, props in json.load(file(SERVERS_JS)).items():
        # fab requires a FQDN 
        hostname += '.okfn.org'
        
        servers['all'].append(hostname)

        for name, value in props.items():
            if name in ['location', 'owner', 'provider']:
                servers['%s::%s' % (name,value)].append(hostname)
    return dict(servers)
        
if __name__ == '__main__':
    print pprint.pprint(get_roles())
