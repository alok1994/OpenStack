import pytest
import unittest
import json
import wapi_module
import re
import time
import util
import os
from netaddr import IPNetwork

tenant_name = 'admin'
network = 'Network'
subnet_name = "Snet"
subnet = "10.2.0.0/24"

class TestOpenStackCases(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	pass

    @pytest.mark.run(order=1)	
    def test_Add_Network_OpenStack_Side(self):
        proc = util.utils(tenant_name)
        proc.create_network(network)
	flag = proc.get_network_name(network)
	assert flag == network

    @pytest.mark.run(order=2)
    def test_Add_Subnet_OpenStack(self):
	proc = util.utils(tenant_name)
	proc.create_subnet(network, subnet_name, subnet)
	flag = proc.get_subnet_name(subnet_name)
	assert flag == subnet_name
    
    @pytest.mark.run(order=3)
    def test_Validate_Network_From_NIOS(self):
	flag = False	
	proc = wapi_module.wapi_request('GET',object_type = 'network',params="?network="+subnet)
	if (re.search(r""+subnet,proc)):
	    flag = True
	assert flag, "Network creation failed "
        	
    @pytest.mark.run(order=4)
    def test_Validate_NIOS_EAs_Cloud_API_Owned_CMP_Type(self):
	proc = wapi_module.wapi_request('GET',object_type = 'network',params="?network="+subnet)
	resp = json.loads(proc)
	ref_v = resp[0]['_ref']
	EAs = json.loads(wapi_module.wapi_request('GET',object_type = ref_v + '?_return_fields=extattrs'))
	assert EAs['extattrs']['Cloud API Owned']['value'] == 'True' and EAs['extattrs']['CMP Type']['value'] == 'OpenStack'

    @pytest.mark.run(order=5)
    def test_Validate_NIOS_EAs_Network_Name_Network_ID_Subnet_Name_Subnet_ID(self):
        proc = wapi_module.wapi_request('GET',object_type = 'network',params="?network="+subnet)
	session = util.utils(tenant_name)
	Net_name = session.get_network_name(network)
	Net = session.get_net_id(network)
	Net_ID = Net[0]
	Sub_name = session.get_subnet_name(subnet_name)
	Snet_ID = session.get_subnet_id(subnet_name)
	resp = json.loads(proc)
        ref_v = resp[0]['_ref']
        EAs = json.loads(wapi_module.wapi_request('GET',object_type = ref_v + '?_return_fields=extattrs'))
        assert EAs['extattrs']['Network Name']['value'] == Net_name and \
               EAs['extattrs']['Network ID']['value'] == Net_ID and \
               EAs['extattrs']['Subnet Name']['value'] == Sub_name and \
               EAs['extattrs']['Subnet ID']['value'] == Snet_ID and \
               EAs['extattrs']['Network Encap']['value'] == 'vxlan' 

    @pytest.mark.run(order=6)
    def test_validate_NIOS_Tenant_ID_Tenant_Name(self):
	proc = wapi_module.wapi_request('GET',object_type = 'network',params="?network="+subnet)
        session = util.utils(tenant_name)
        tenant = session.get_net_id(network)
        tenant_ID = tenant[1]
	resp = json.loads(proc)
        ref_v = resp[0]['_ref']
        EAs = json.loads(wapi_module.wapi_request('GET',object_type = ref_v + '?_return_fields=extattrs'))
        assert EAs['extattrs']['Tenant ID']['value'] == tenant_ID and \
	       EAs['extattrs']['Tenant Name']['value'] == 'admin'

    @pytest.mark.run(order=7)
    def test_Validate_Router(self):
	proc = wapi_module.wapi_request('GET',object_type = 'network',params="?network="+subnet)
	resp = json.loads(proc)
        ref_v = resp[0]['_ref']
	options = json.loads(wapi_module.wapi_request('GET',object_type = ref_v + '?_return_fields=options'))
	route_list = options['options']
	list_route = route_list[1]
	route_nios = list_route['value']
	ip = IPNetwork(subnet).iter_hosts()
        route = str(ip.next())
	assert route_nios == route
