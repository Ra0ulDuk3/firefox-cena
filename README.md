

## Requirements

The tool must perform at least 3 discrete steps in an automated fashion such that the output from step 1 is the input to step 2.
1) In class demonstration of the tool actually completing successfully (the tool must work)
2) In class presentation about the tool – what it does, why it does it, and any limitations or reasons for configuration choices  (15 minute hard time limit)
3) Paper that 1) describes the tool, 2)  notes any problems you encountered during creation/testing/usage, and 3) any ideas you could implement to improve or enhance the functionality.  

A simple example of a tool would be a user enumeration tool that 1) pings a network range for live hosts, 2) scans for udp port 161, and 3) walks the snmp tree and parses usernames.   The analysis in the paper might include problems you encountered getting snmpwalk to work, why you chose certain default community strings, and then ideas that version 2.0 of your tool would also add SMTP and finger enumeration.


## Deadlines
- April 7th – deadline to submit your project idea to prosise@cs.utexas.edu for approval
- April 28 – In class presentations due
- May 5 – Final papers and code submitted

## Draft Ideas 

### Speer

#### Dependencies
- List of target sites

#### Steps

1. Setup
    - Clone target sites
    - fabricate DNS entries
    - initialize collection database

2. Enumerate Networks 
    - Scan for WPA2 networks  

3. Gain Network Access
    - deauth clients 
    - dictionary attack pre-shared key

4. Collect Network Data 
    - sniff traffic to gather:
        - clients
        - total traffic
        - percent of traffic that is interacting over ports 80 or 443 with targets

5. Present Options (this is where I would have liked for it to be parallelized)

6. Phish
    - for all targeted sites:
        - setup webserver that speaks to our database
        - DNS poison
        - forward credentials into site once we have sent to our database


### Hendrix
1. Enumerate Networks
2. Gain Access
    - for all WPA2 networks, deauth 
4. Detect browser, if firefox and debian-based; 
   - poison dns, point every single site to a 'firefox needs update, cant work' 
   - user downloads paylod in deb file called firefox_11_2.deb
   - Instructions for download 
- payload: bash script that renames their bashrc to .old.bashrc and puts a new bashrc that remaps every key to an annoying ass operation like opening a firefox window and playing https://www.youtube.com/watch?v=m78e1WBnlsE

Hendrix
===========================
