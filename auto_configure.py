import sys
import json
import os
import random
import string

try:
    shadowsocks_config=open('D:/shadowsocks.json','r+')
    config=json.load(shadowsocks_config)
except:
    print 'opps'
templete={'server':'0.0.0.0','port_password':{},'method':'aes-256-cfb','local_port':'1080','timeout':'30'}

def initalize():
    global new_config
    
    new_config=templete
    
    temp1=raw_input('Your server ip address (skip by press [Enter]): ')
    if not temp1:
        temp1='0.0.0.0'
    new_config['server']=temp1
    del temp1
    
    temp1=raw_input('Encrypt method (default: aes-256-cfb): ')
    if not temp1:
        temp1='aes-256-cfb'
    new_config['method']=temp1
    del temp1

    temp1=raw_input('Timeout (default: 30): ')
    if not temp1:
        temp1='30'
    new_config['timeout']=temp1
    del temp1

    temp1=raw_input('Local Port (default: 1080): ')
    if not temp1:
        temp1='1080'
    new_config['local_port']=temp1
    del temp1

    asd=True
    while asd:
        add_member()
        ask_continue=raw_input('Do you still need to add ports? (Y/N): ')
        if ask_continue=='N' or ask_continue=='n' or ask_continue=='':
            asd=False

    temp_config=json.dumps(new_config)
    config_write(temp_config)

    return new_config

def add_member(port=None,passwd=''):
    if not port:
        if not passwd:
            
            port=raw_input('Please enter the port: ')
            if not port:
                message=raw_input('Do you want a random port? (Y/N)')
                if message=='Y' or message=='y' or message=='':
                    port=random.randrange(9000,65536)
                else:
                    port='9001'

            passwd=raw_input('Password for this port: {} :'.format(port))
            if not passwd:
                for i in range(10):
                    passwd=passwd+random.choice(string.letters)
            new_config['port_password'][str(port)]=passwd
    else:
        if not passwd:
            str(passwd)
            for i in range(10):
                passwd+=random.choice(string.letters)
        try:
            port=int(port)
            if port<100000 and port>9:
                new_config['port_password'][str(port)]=passwd
        except ValueError:
            raise('Port is not valuable!')

def config_write(pending_config):
    #Must be json standard dictionary
    file_detected=False
    permitted=False
    if os.path.exists('/etc/shadowsocks.json'):
        file_detected=True
        choice=raw_input('This step would override the old config file. Continue? (Y/N): ')
        if choice=='Y' or choice=='y' or choice=='':
            permitted=True
        else:
            permitted=False

    if file_detected and permitted:
        os.remove('/etc/shadowsocks.json')
        os.system('touch {}'.format('/etc/shadowsocks.json'))
        config_file=open('/etc/shadowsocks.json','w+')
    elif file_detected and not permitted:
        file_path=raw_input('Please enter another path for the config (default: /): ')
        if not file_path:
            file_path='/'
        os.system('touch {}'.format(file_path))
        config_file=open(file_path,'w+')
    else:
        os.system('touch {}'.format('/etc/shadowsocks.json'))
        config_file=open('/etc/shadowsocks.json','w+')

    config_file.write(str(pending_config))

    config_file.close()

def firewall_unlock():
    for i in new_config['port_password'].keys():
        result=os.system('sudo firewall-cmd --add-port={}/tcp --permanent'.format(i))
        if result=='success':
            continue
        else:
            print('Failed to bind port {} in firewall-cmd'.format(i))
            
        os.system('firewall-cmd --add-port={}/udp --permanent'.format(i))
        del result
        result=os.system('sudo iptables -A INPUT -p tcp --dport {} -j ACCEPT'.format(i))
        if result=='':
            continue
        else:
            print 'Something may happened during adding rules to iptables. Please notice. '
        os.system('sudo iptables -A INPUT -p udp --dport {} -j ACCEPT'.format(i))
        os.system('sudo firewall-cmd --reload')

def ipforward():
    os.system('sudo echo "1"> /proc/sys/net/ipv4/ip_forward')
    #ip_forward
    if not os.path.exists('/etc/sysconfig/network'):
        os.system('touch {}'.format('/etc/sysconfig/network'))
    network_config_file=open('/etc/sysconfig/network','w+')
    network_config_file.write('FORWARD_IPV4="YES"')
        
        
def startup_file(config_file_path='/etc/shadowsocks.json'):
    content=['sudo echo "1"> /proc/sys/net/ipv4/ip_forward','ssserver -c "{}"'.format(config_file_path)]
    file_path=raw_input('Please enter the startup file path (default: /start.sh): ')
    if not file_path:
        file_path='/start.sh'
    if not os.path.exists(file_path):
        os.system('touch {}'.format(file_path))
        File=open(file_path,'w+')
        for i in range(len(content)):
            File.write(content[i]+'\n')
        
def server_reg():
    path='/etc/systemd/system/shadowsocks.service'
    lines=['[Unit]','Description=Shadowsocks','[Service]','TimeoutStartSec=0','ExecStart=/usr/bin/ssserver -c /etc/shadowsocks.json','[Install]','WantedBy=multi-user.target']
    with open(path,'w+') as files:
        for line in lines:
            files.write(line+'\n')
    os.system('sudo systemctl enable shadowsocks')
    os.system('sudo systemctl start shadowsocks')
    print 'Service registed!'
    
def main():
    crazy_list=initalize()
    firewall_unlock()
    ipforward()
    startup_file()
    crazy_list_keys=crazy_list['port_password'].keys()
    for i in crazy_list_keys:
        print 'Port: ',i
        print 'Password: ',crazy_list['port_password'][i],'\n'
    server_reg()
if __name__ == "__main__":
    main()

    
