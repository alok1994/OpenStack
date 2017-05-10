import pexpect
import os
import test_add_network

def test_log_in(IP=''):
    fout = open('log-in.txt','w+')
    proc = pexpect.spawn('ssh stack@'+IP)
    proc.logfile_read = fout
    answer = '(yes/no)?'
    prompt = '.*assword:'
    i = proc.expect([answer,prompt])
    if i == 0:
            proc.expect('.*assword:')
            proc.sendline('stack')
    if i==1:
            proc.sendline('yes')
    return proc


#test_log_in(IP='10.39.12.79')
