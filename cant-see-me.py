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



def monitor_mode(interface, log):
    '''
    Sets the chosen network interface to monitor mode using airmon-ng
    '''
    try:
        cmd = ['sudo', 'airmon-ng', 'start', interface]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        output = result.stdout
        mon_interface = parse_monitor_interface(output)
        return mon_interface

    except:
        print("Error occured during Interface Initialization")

def parse_monitor_interface(output):
    '''
    given the output from airmon-ng, finds the new name of the 
    network interface as a monitor mode interface 
    '''
    output = output.split('\n')
    for idx in range(0, len(output)):
        line = output[idx]
        if 'PHY' in line and 'Interface' in line: 
            # skip a line and we will find our new monitor interface
            mon_interface = output[idx + 2]
            mon_interface = mon_interface.split("\t")[1]
            return mon_interface
    print('Error finding monitor interface')
    exit()


def collect_target_data(mon_interface):
    '''
    Given an interface which has been put into monitor mode, 
    performs a 30 second wirless packet capture 
    '''



# make sure interface is working 

# check out the internet traffic 

# find out what access point to imitate

# setup dnschef

# deauth client


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
    # check for root access
    check_root()
    # get the network interface from the user
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='network interface to use', type=str)
    args = parser.parse_args()
    interface = args.interface
    # change the network card to monitor mode
    monitor_mode(interface, log)



    #except Exception: 
    #    exit()



if __name__ == '__main__':
    main()
