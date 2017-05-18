from novaclient.client import Client
from neutronclient.v2_0 import client
import json
import wapi_module 
import os, sys
import ConfigParser
import logger 

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
#        logger.info("Created Network '%s'", network_name)
#        logger.debug("Network ID of '%s' : %s", network_name, network_id)
    
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

    def get_network_name(self, nw_name):
	'''
	Retrun the Network Name
	'''
	nw = self.get_networks()
	for n in nw:
	    if n['name'] == nw_name:
	        return nw_name
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

    def launch_instance(self, name, nw_name):
        """
        Return Server Object if the instance is launched successfully
        
        It takes Instance Name and the Network Name it should be associated with as arguments.
        """
        image = self.nova_client.images.find(name="cirros-0.3.3-x86_64-disk")
        flavor = self.nova_client.flavors.find(name="m1.tiny")
        net_id, tenant_id = self.get_net_id(nw_name)
        nic_d = [{'net-id': net_id}]
        instance = self.nova_client.servers.create(name=name, image=image,
                                                   flavor=flavor, nics=nic_d)
        logger.info("Launched Instance '%s', waiting for it to boot", name)
        time.sleep(60)
        return instance

    def get_servers_list(self):
        """
        Return List of Servers
        """
        return self.nova_client.servers.list()

    def get_server(self, name):
        """
        Return Server Object for a given instance name
        """
        servers_list = self.get_servers_list()
        server_exists = False
        for s in servers_list:
            if s.name == name:
                logger.debug("Instance '%s' exists", name)
                server_exists = True
                break
        if not server_exists:
            return None
        else:
            return s

    def terminate_instance(self, name):
        """
        Terminates an instance
        It takes Instance Name as argument.
        """
        server = self.get_server(name)
        if server:
            self.nova_client.servers.delete(server)
            time.sleep(60)
            logger.info("Terminated Instance '%s'", name)
        else:
            logger.error("Instance '%s' does not exist", name)

    def delete_subnet(self, subnet_name):
        """
        Deletes a Subnet
        It takes Subnet Name as argument.
        """
        subnets = self.neutron_client.list_subnets()
        logger.debug("Subnets details before deleting '%s' : %s", subnet_name, subnets)
        for s in subnets['subnets']:
            if s['name'] == subnet_name:
                self.neutron_client.delete_subnet(s['id'])
                logger.info("Deleted Subnet '%s'", subnet_name)
        subnets = self.neutron_client.list_subnets()
        logger.debug("Subnets details after deleting '%s' : %s", subnet_name, subnets)

    def delete_network(self, network_name):
        """
        Deletes a Network
        It takes Network Name as argument.
        """
        net_id, tenant_id = self.get_net_id(network_name)
        if net_id:
            netw = self.neutron_client.delete_network(net_id)
            logger.debug("Network ID of '%s' : %s", network_name, net_id)
            logger.info("Deleted Network '%s'", network_name)
        else:
            logger.error("Network '%s' does not exist", network_name)

    def get_subnets(self):
	"""
        Return List of Subnets
        """
        netw = self.neutron_client.list_subnets()
        return netw['subnets']

    def get_subnet_id(self, sn_name):
        """
        Return Subnet ID for the given subnet name
        """
        nw = self.get_subnets()
        for n in nw:
            if n['name'] == sn_name:
                return n['id']
        return None

    def get_subnet_name(self,sn_name):
        '''
	Return Subnet Name
	'''
	sn = self.get_subnets()
	for n in sn:
		if n['name'] == sn_name:
		    return sn_name
	return None
     
    def create_router(self, router_name, network_name):
            net_id1, tenant_id = self.get_net_id(network_name)
            r = {'router': {'name': router_name, 'admin_state_up': True, 'external_gateway_info': {'network_id': net_id1}}}
            router = self.neutron_client.create_router(body=r)
            rt_dict = router['router']
            rt_id = rt_dict['id']
            logger.info("Created Router '%s'", router_name)
            logger.debug("Router ID of '%s' : %s", router_name, rt_id)

    def get_routers(self):

        routers_list = self.neutron_client.list_routers(retrieve_all=True)
        return routers_list['routers']

    def get_rout_id(self, rt_name):

        rt = self.get_routers()
        for n in rt:
            if n['name'] == rt_name:
                return n['id']
        return None

    def delete_router(self, router_name):
        router_id = self.get_rout_id(router_name)
        self.neutron_client.delete_router(router=router_id)

    def create_port(self, interface_name, network_name):
        net_id, tenant_id = self.get_net_id(network_name)
        port = {'port': {'name': interface_name, 'admin_state_up': True, 'network_id': net_id}}
        port_info = self.neutron_client.create_port(body=port)

    def get_ports(self):
        ports = self.neutron_client.list_ports()
        return ports['ports']

    def get_port_id(self, interface_name):
        pt = self.get_ports()
        for n in pt:
            if n['name'] == interface_name:
                return n['id']
        return None

    def get_instance_port_id(self, ip):
        pt = self.get_ports()
        for n in pt:
            if n['fixed_ips'][0]['ip_address'] == ip:
                return n['id']
        return None

    def add_router_interface(self, interface_name, router_name):
        router_id = self.get_rout_id(router_name)
        port_id = self.get_port_id(interface_name)
        body = {'port_id':port_id}
        rt = self.neutron_client.add_interface_router(router=router_id, body=body)
        logger.info("Created Internal Interface '%s' under the Router '%s'", interface_name, router_name)

    def remove_router_interface(self, interface_name, router_name):
        router_id = self.get_rout_id(router_name)
        port_id = self.get_port_id(interface_name)
        body = {'port_id':port_id}
        rt = self.neutron_client.remove_interface_router(router=router_id, body=body)
        logger.info("Deleted Internal Interface '%s' under the Router '%s'", interface_name, router_name)

    def add_floating_ip(self, instance_name):
        floating_ip = self.nova_client.floating_ips.create()
        instance = self.nova_client.servers.find(name=instance_name)
        instance.add_floating_ip(floating_ip)

    def delete_floating_ip(self, instance_name):
        fip_list = self.nova_client.floating_ips.list()
        floating_ip = fip_list[0].ip
        floating_ip_id = fip_list[0].id
        instance = self.nova_client.servers.find(name=instance_name)
        instance.remove_floating_ip(floating_ip)
        self.nova_client.floating_ips.delete(floating_ip_id)

    def get_instance_name(self, instance):
        name = instance.name
        return name

    def get_instance_ips(self, instance_name):
        instance = self.nova_client.servers.find(name=instance_name) 
        ips = self.nova_client.servers.ips(instance.id)
        return ips

    def interface_attach(self, server, network):
        net_id, tenant_id = self.get_net_id(network)
        iface = self.nova_client.servers.interface_attach(port_id='',fixed_ip='',server=server,net_id=net_id,)
        return iface

    def interface_detach(self, server, port_id):
        self.nova_client.servers.interface_detach(server=server, port_id=port_id) 

