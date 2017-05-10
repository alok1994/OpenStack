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
    def test_Add_Network_with_Subnet_OpenStack_side(self):
        proc = util.utils(tenant_name)
        proc.create_network(network)
	proc.create_subnet(network, subnet_name, subnet)
	
