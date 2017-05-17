import os
import json

conn = None
# uri = 'postgres://postgres:password@host.pcfdev.io:5431/postgres'
uri = None

### Extract the database URI value from VCAP_SERVICES
def getDatabaseUri():

    global uri

    if uri is not None:
        return uri

    if 'VCAP_SERVICES' in os.environ:
        print('VCAP_SERVICES found in os.environ')
        decoded_config = json.loads(os.environ['VCAP_SERVICES'])
    else:
        print('VCAP_SERVICES NOT found in os.environ')
        return os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://ras_party:password@localhost:5431/postgres')

    for key, value in decoded_config.items():
        print('Inspecting key: "' + str(key) + '" with value: ' + str(value))
        if decoded_config[key][0]['name'] == 'db_ras_party':
            creds = decoded_config[key][0]['credentials']
            uri = creds['uri']
            print('Postgres DATABASE uri: ' + uri)
            return uri