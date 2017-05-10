from novaclient.client import Client
from neutronclient.v2_0 import client
import json
import wapi_module 
import os
import ConfigParser
import logging 

#CONF = "config.ini"
#parser = ConfigParser.SafeConfigParser()
#parser.read(CONF)
#GRID_VIP = parser.get('Default', 'GRID_VIP')
#USERNAME = parser.get('Default', 'USERNAME')
#PASSWORD = parser.get('Default', 'PASSWORD')
#ADMIN_USERNAME = parser.get('Default', 'ADMIN_USERNAME')
#ADMIN_PASSWORD = parser.get('Default', 'ADMIN_PASSWORD')
#WAPI = parser.get('Default', 'WAPI_VERSION')
os.system('export OS_USERNAME=admin')
os.system('export OS_PASSWORD=admin')
os.system('export OS_TENANT_NAME=admin')
os.system('export OS_AUTH_URL=http://10.39.12.79:35357/v2.0')

class utils:
    def __init__(self, tenant_name):
        self.tenant_name = tenant_name
        credentials = {}
        credentials['username'] = os.environ['OS_USERNAME']
        credentials['auth_url'] = os.environ['OS_AUTH_URL']
        nova_credentials = credentials
        nova_credentials['api_key'] = os.environ['OS_PASSWORD']
        nova_credentials['project_id'] = self.tenant_name
    	nova_credentials['version'] = '2'
        self.nova_client = Client(**nova_credentials)
        neutron_credentials = credentials
        neutron_credentials['tenant_name'] = self.tenant_name
        neutron_credentials['password'] = os.environ['OS_PASSWORD']
        self.neutron_client = client.Client(**neutron_credentials)

    def create_network(self,network_name, external=False):
        nw = {'network': {'name': network_name, 'admin_state_up': True, 'router:external' : external}}
        netw = self.neutron_client.create_network(body=nw)
        net_dict = netw['network']
        network_id = net_dict['id']
 #   logger.info("Created Network '%s'", network_name)
  #  logger.debug("Network ID of '%s' : %s", network_name, network_id)

    def get_networks(self):
        netw = self.neutron_client.list_networks()
        return netw['networks']

    def get_net_id(self, nw_name):
        nw = self.get_networks()
        for n in nw:
            if n['name'] == nw_name:
                return n['id'], n['tenant_id']
        return None
