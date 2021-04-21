import csv 
import time
import subprocess
import os
import argparse

def check_root():
    """
    Checks if program is run by the root user.
    """
    if os.geteuid() != 0:
        exit("run it as root")


def print_welcome():
    """
    Welcomes the user to the program
    """
    print("Firefox Cena allows the user")



def monitor_mode(interface):
    '''
    Sets the chosen network interface to monitor mode using airmon-ng
    '''
    try:
        print("[-] initializing network interface...")
        cmd = ['sudo', 'airmon-ng', 'start', interface]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        output = result.stdout
        mon_interface = parse_monitor_interface(output)
        print("[+] initialized network interface!")
        return mon_interface

    except:
        print("Error occured during Interface Initialization")

def parse_monitor_interface(output):
    '''
    given the output from airmon-ng, finds the new name of the 
    network interface as a monitor mode interface 
    '''
    print("[-] finding new monitor interface...")
    output = output.split('\n')
    for idx in range(0, len(output)):
        line = output[idx]
        if 'PHY' in line and 'Interface' in line: 
            # skip a line and we will find our new monitor interface
            mon_interface = output[idx + 2]
            mon_interface = mon_interface.split("\t")[1]
            print("[+] found new monitor interface!")
            return mon_interface
    print('[!] Error finding monitor interface')
    exit()


def collect_target_data(mon_interface, log_prefix):
    '''
    Given an interface which has been put into monitor mode, 
    performs a 30 second wirless packet capture using airmon-ng

    args:
        mon_interface(str): name of the monitor mode enabled network interface
        log_prefix(str): name of prefix for log files 

    return:
        networks(dictionary): target data to be presented to user; total packets captured:(bssid, essid)
    '''

    print('[-] aggregating data for potential target networks...')
    networks = {}

    log_file = log_prefix + '-01.csv'
    print(mon_interface)
    cmd = 'sudo airodump-ng {} -w {}'.format(mon_interface, log_prefix)
    # execute for 30 seconds, then kill

    proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
    time.sleep(1)
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

    print('[+] aggregated data for potential target networks!')
    return networks


def user_network_decision(network_data):
    '''
    Given a dictionary containing bssids as names and a tuple
    containing total packets and essid, allows to user to decide which network 
    they would like to clone during the evil twin attack
    '''

    print("\n\ntargets found for our evil-twin attack!\nthe higher the number of packets transmitted the more likely a victim on the network will be found\nbe sure to choose a network which you own or have permission to be monkeying with\n ")
    print("Here are the available target networks:")

    trimmed_data = {int(key.replace(" ", "")): val for key, val in network_data.items()}
    keys = [*trimmed_data]
    keys.sort(reverse=True)

    # sort in descending order

    print ('[index]: Packets -- BSSID -- ESSID')
    print ('--------------------------------------------------')
    for idx in range(0,len(keys)):
        packets = keys[idx]
        bssid = trimmed_data[keys[idx]][0]
        essid = trimmed_data[keys[idx]][1]
        print("[{}]: {} -- {} -- {}".format(idx, packets, bssid, essid))
    decision = int(input("Enter the number of the network you'd like to clone:"))
    if decision < 0 or decision >= len(keys):
        print("fucked up on the input m8")
        exit()
    else:
        decision = keys[idx]

    return trimmed_data[decision]


    
def clone_network(network, interface, channel=1):

    pass


def deauth_clients(bssid, interface):
    pass


def bridge_internet():
    pass

def launch_evil_server():
    pass

def redirect_dns():
    pass
# setup dnschef

def restore_dns():
    pass


def managed_mode(mon_interface):
    '''
    Returns the network interface to managed mode
    '''

def main():
    """
    Main Driver
    """
    #try:
    # create the log
    #log = open("./logs/process.log", "a")
    dump_prefix = 'dump'
    # check for root access
    check_root()
    # get the network interface from the user
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='network interface to use', type=str)
    args = parser.parse_args()
    interface = args.interface
    # change the network card to monitor mode
    mon_interface = monitor_mode(interface)
    # capture wireless packets (recon)
    network_data = collect_target_data(mon_interface, dump_prefix)
    # present user with option of network to clone and allow for them to decide
    target_network = user_network_decision(network_data)
    # create the evil twin
    clone_network(target_network, mon_interface)
    

    #except Exception: 
    #    exit()



if __name__ == '__main__':
    main()
