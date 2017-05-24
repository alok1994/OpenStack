import pytest
import unittest
import json
import wapi_module
import re
import time
import util

tenant_name = 'admin'
network = 'Net1'
subnet_name = "Snet1"
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
	proc = wapi_module.wapi_request('GET',object_type = 'network',params='?network='+'subnet')
	

    @pytest.mark.run(order=4)
    def test_Validate_NIOS_EAs_Cloud_API_Owned_CMP_Type(self):
	pass

    @pytest.mark.run(order=5)
    def test_Validate_NIOS_EAs_Network_Name_Network_ID_Subnet_Name_Subnet_ID(self):
	pass

    @pytest.mark.run(order=6)
    def test_Validate_Router(self):
	pass

