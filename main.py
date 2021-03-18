import requests
import pandas as pd
import yaml
import datetime

time = datetime.datetime.now()

with open(r'./env_vars.yml') as file:
    vars = yaml.load(file, Loader=yaml.FullLoader)

m_headers = {'X-Cisco-Meraki-API-Key': vars['meraki_dash']['meraki_apikey']}
m_baseUrl = vars['meraki_dash']['m_baseUrl']

#get orginization #
org_response = requests.request("GET", f'{m_baseUrl}/organizations/', headers=m_headers)
org = org_response.json()

#uncomment to test return value
#print(org[0]["id"])

#create iterable list of all devices and then create filtered categories
dev_response = requests.request("GET", f'{m_baseUrl}/organizations/{org[0]["id"]}/devices/', headers=m_headers)
if 'json' in dev_response.headers.get('Content-Type'):
    devices = dev_response.json()
    switches = [device for device in devices if device['model'][:2] == 'MS']
    cameras = [device for device in devices if device['model'][:2] == 'MV']
    wireless = [device for device in devices if device['model'][:2] == 'MR']
    appliance = [device for device in devices if device['model'][:2] == 'MX']
    sensor = [device for device in devices if device['model'][:2] == 'MT']

    #uncomment to test return values
    #print(switches)
    #print(wireless)
    #print(cameras)
    #print(appliance)

else:
    print('Response content is not in JSON format.')


# Call switch port API
for serial in switches:
    switch_req = requests.get(f'{m_baseUrl}/devices/{serial["serial"]}/switch/ports', headers = m_headers)
    if 'json' in switch_req.headers.get('Content-Type'):
       switch_ports = switch_req.json()

    # create data storage object
       port_data = {'Switch' : [], 'Port' : [], 'Name' : [], 'Tags' : [], 'Enabled' : [], 'PoE Enabled' : [],
                 'Type' : [], 'VLAN' : [], 'Voice VLAN' : [], 'Allowed VLANs' : [], 'Isolation Enabled' : [],
                 'RSTP Enabled': [], 'STP Guard': [], 'Link Negotiation' : []}

    # populate the data storage object
       for port in switch_ports:
           port_data['Switch'].append(serial['serial'])
           port_data['Port'].append(port['portId'])
           port_data['Name'].append(port['name'])
           port_data['Tags'].append(port['tags'])
           port_data['Enabled'].append(port['enabled'])
           port_data['PoE Enabled'].append(port['poeEnabled'])
           port_data['Type'].append(port['type'])
           port_data['VLAN'].append(port['vlan'])
           port_data['Voice VLAN'].append(port['voiceVlan'])
           port_data['Allowed VLANs'].append(port['allowedVlans'])
           port_data['Isolation Enabled'].append(port['isolationEnabled'])
           port_data['RSTP Enabled'].append(port['rstpEnabled'])
           port_data['STP Guard'].append(port['stpGuard'])
           port_data['Link Negotiation'].append(port['linkNegotiation'])

    # Build switch port dataframe
       switch_port_df = pd.DataFrame(data = port_data)


    # Write dataframe to csv
       switch_port_df.to_csv(path_or_buf = serial['serial'] + '_ports-' + str(time) + '.csv', index = False)

       print(f'The switch port information has been stored in {serial["serial"]}_ports.csv')


    else:
        print('Response content is not in JSON format.')