import pytest
import unittest
import json
import wapi_module
import re
import time
import util

tenant_name = 'admin'
network = 'Net1'

class TestOpenStackCases(unittest.TestCase):
    @classmethod
    def setup_class(cls):
	pass

    @pytest.mark.run(order=1)	
    def test_Add_network_OpenStack_side(self):
        proc = util.utils(tenant_name)
        proc.create_network(network)
	
