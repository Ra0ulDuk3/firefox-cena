import subprocess




# make sure interface is working 

# check out the internet traffic 
subprocess.run

# find out what access point to imitate

# setup dnschef

# deauth client

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


def main():
    """
    Main Driver
    """
    try:
        check_root()



    except KeyboardInterrput:
        exit()



if __name__ == '__main__':
    main()
