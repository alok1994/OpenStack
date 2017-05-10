import log_in
import pexpect

def test_add_subnet():
    session = log_in.test_log_in(IP='10.39.12.79')
    session.expect('.*\$')
    session.sendline('source /opt/devstack/openrc admin admin')
    session.expect('.*\$')
    import pdb
    pdb.set_trace()
    session.sendline('neutron subnet-create Net1 --name Subnet1 --allocation-pool start=10.2.0.2,end=10.2.0.250 --disable-dhcp --gateway 10.2.0.1 10.2.0.0/24')
    session.expect('.*\$')
    data = session.after
    #spl = data.split('|')
    session.close()

if __name__ == '__main__':
    test_add_subnet()


