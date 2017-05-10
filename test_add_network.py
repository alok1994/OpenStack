import commands
import log_in

def test_add_network():
    session = log_in.test_log_in(IP='10.39.12.79') 
    session.expect('.*\$')
    session.sendline('source /opt/devstack/openrc admin admin')
    session.expect('.*\$')
    session.sendline('neutron net-create Net1')
    session.expect('.*\$')
    session.close()

if __name__ == '__main__':
    test_add_network()
