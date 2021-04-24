firefox cena
============

### Steps
1. Find out access point we want to imitate  (airmon-ng)
2. Imitate the access point  (airebase-ng)
3. setup dnschef to redirect all traffic to my server (update firefox page),except install instructions page, forward it to my install instructions
4. Deauth client (aireplay-ng)
5. Client joins, installs my payload 
    - payload: bash script that installs dependencies, hides assets, and sets crontabs  




Firefox Cena 
===============

## Abstract

This tool allows a user to gain remote code execution with root priviledges through the deployment of an evil-twin rogue access point, DNS poisioning, and phishing attack. Firefox Cena allows the user to carry out the following steps:

1. **Network Enumeration**: Enumerate local wireless networks in order to find a network worth impersonating.
2. **Network Spoofing**: Execute an 'Evil-Twin' attack, by spoofing the BSSID and ESSID of the target network.
3. **Traffic Redirection**: Redirect all domains to our evil apache server that contains a malicious 'firefox needs update' site which will prompt clients to download payload disguised as firefox update
4. **Deauthentication**: Deauthenticate clients of legitimate network so that clients can connect to spoofed network.
5. **Payload Installation**: Upon execution of update script by client, installs TTS application and image viewer as well as minutely crontab which harasses client by running TTS in background and displaying an excessive amount of images of john cena 



## Method 

https://www.kalitutorials.net/2014/07/evil-twin-tutorial.html

### Interface Initialization

Firefox Cena takes a single command line argument which dictates the network interface to be used for the procedure. 

`python3 cant-see-me.py <network-interface>`

In order to allow execution of the evil twin attack and direct all of the victims web traffic to our webserver, the first subroutine executed by FC is setting the network interface to Monitor mode using airmon-ng.

### Network Enumeration

The first phase of Firefox Cena consists of identifying potential networks that can be spoofed. This is done by performing a packet capture on the locally accessible wireless networks using airodump to capture key information to present to the user, namely; BSSIDs, ESSIDs, and the number of data packets sent in the past 30 seconds.

FIXME:add image of output
![]()

### Network Spoofing

### Traffic Redirection

### Deauthentication

### Payload Installation

## Evaluation 

### Issues 

### Future Improvements
- would be cool to have silent mode 
