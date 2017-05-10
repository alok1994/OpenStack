from novaclient.client import Client
from neutronclient.v2_0 import client
import json
import wapi_module 
import os, sys
import ConfigParser
import logging 

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
	''''
	Add a Network OpenStack Side
	    Pass the Network Name as Arg
	'''
        nw = {'network': {'name': network_name, 'admin_state_up': True, 'router:external' : external}}
        netw = self.neutron_client.create_network(body=nw)
        net_dict = netw['network']
        network_id = net_dict['id']
 #   logger.info("Created Network '%s'", network_name)
  #  logger.debug("Network ID of '%s' : %s", network_name, network_id)
    
    def get_networks(self):
        """
        Return List of Networks
        """
        netw = self.neutron_client.list_networks()
        return netw['networks']

    def get_net_id(self, nw_name):
        """
        Return Network ID for the given Network name
        """
        nw = self.get_networks()
        for n in nw:
            if n['name'] == nw_name:
                return n['id'], n['tenant_id']
        return None

    def create_subnet(self, network_name, subnet_name, subnet):
        """
        Creates a Subnet
        It takes Network Name, Subnet Name and Subnet as arguments.
        For Example:-
        project.create_subnet("Network1", "Subnet-1-1", "45.0.0.0/24")
        """
        net_id, tenant_id = self.get_net_id(network_name)
        body_create_subnet = {'subnets': [{'name': subnet_name, 'cidr': subnet, 'ip_version': 4, 'tenant_id': tenant_id, 'network_id': net_id}]}
        try:
            subnet = self.neutron_client.create_subnet(body=body_create_subnet)
            logger.info("Created Subnet '%s' under the Network '%s'", subnet_name, network_name)
        except:
            print("Failed to create Subnet : ", sys.exc_info()[0])

