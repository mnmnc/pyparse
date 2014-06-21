#!/usr/bin/env python3.4
 
# IMPORTS
import re
import socket
import pprint
from colorama import init, Fore, Back, Style
 
# VARS
log_path = '/var/log/auth.log'
hosts=[]
full_hosts_data=[]
previous_ip = ""
previous_host = ""
 
# ADJUSTING TO FIXED LENGTH
def adjust_item( str, i ):
    if len(str) < i:
        for j in range(i-len(str)):
            str = str + " "
    return str
 
# AS THE NAME SAYS
def get_hostname( ip ):
    global previous_ip
    global previous_host
    if previous_ip == ip:
        return previous_host
    else:
        try:
            new_host = socket.gethostbyaddr(ip)
            previous_ip = ip
            previous_host = new_host[0]
            return new_host[0]
        except Exception:
            new_host = ip
            previous_ip = ip
            previous_host = ip
            return new_host
 
# RETURNING FIRST FIVE ACCOUNTS AND NUMBER OF ALL ACCOUNTS TRIED
def first_5( parsed_string ):
    result_5 = ""
    count_all = 0
    if len( parsed_string.split("|") ) > 5 :
        index = 5
        for item in parsed_string.split("|"):
            if index > 0 and len(item) > 0:
                result_5 = result_5 + "|" + item
                index = index - 1
            if len(item) > 0:
                count_all = count_all + 1
    else:
        for item in parsed_string.split("|"):
            if len(item) > 0:
                result_5 = result_5 + "|" + item
                count_all = count_all + 1
    return (result_5, count_all )
 
# CHECKING PORT RANGE AND NUMBER OF PORTS WITH FAILED PASSWORDS
def port_parser( parsed_string):
    smallest = 66000
    largest = -1
    counter = 0
    for port in parsed_string.split("|"):
        if len(port) > 0:
            if int(port) < smallest:
                smallest = int(port)
            if int(port) > largest:
                largest = int(port)
            counter = counter + 1
    return( largest, smallest, counter )
 
def get_date( my_line ):
    date_words = my_line.split(":")
    date = date_words[0] +":"+ date_words[1] +":"+ ((date_words[2]).split(" "))[0]
    return date
 
def get_ports( my_line ):
    port_words = my_line.split(" port ")
    port = (port_words[1]).split(" ")
    return port[0]
 
def get_username( my_line ):
    username_words = my_line.split("invalid user ")
    username = (username_words[1]).split(" ")
    return username[0]
 
def get_username2( my_line ):
    username_words = line.split("Failed password for ")
    username = (username_words[1]).split(" ")
    return username[0]
 
def check_distinct(itemlist, my_item):
    item_exists = 0
    my_list = itemlist
    for i in my_list.split("|"):
        if i == my_item:
            item_exists = 1
    if item_exists == 0:
        my_list = my_list + "|" + my_item
    return my_list
 
# READ FILE
with open(log_path, 'rt') as log:
    text = log.read();
 
# COLLECTING HOSTS AND IPS
for line in text.split("\n"):
    if len(line) > 5:
        # PARSE LINE AND ADJUST FIELD LENGTH
        check_1 = line.find("cron:session")
        check_2 = line.find("Disconnecting")
        check_3 = line.find("Address")
        if check_1 == -1 and check_2 == -1 and check_3 == -1:
            break_in = line.find("POSSIBLE BREAK-IN ATTEMPT")
            if break_in != -1:
                words = line.split(" [")
                words2 = (words[1]).split("]")
                host = get_hostname( words2[0] )
                exists_check = 0
                for my_host in hosts:
                    if my_host["ip"] == words2[0]:
                        exists_check = 1
                if exists_check == 0:
                    hosts.append({"ip":words2[0], "hostname":host})
 
for my_host in hosts:
    ports = ""
    accounts = ""
    date = ""
 
    for line in text.split("\n"):
        # CHECK LINES FOR FAILED PASS ATTEMPTS
        if line.find(my_host["ip"]) != -1 and line.find("Failed password") != -1:
 
            if line.find("Failed password for invalid ") != -1:
                username = get_username( line )                 # GET USERNAME
            else:
                username = get_username2( line )                # GET USERNAME
 
            port = get_ports( line )                            # GET PORT USED
            date = get_date( line )                             # GET DATE
            ports = check_distinct(ports, port)                 # SAVE ONLY DISTINCT PORTS
            accounts = check_distinct(accounts, username )      # SAVE ONLY DISTINCT ACCOUNTS
 
    # SAVE ACCTUAL ATTEMPTS
    if len(ports) > 1:
        full_hosts_data.append({
            "ip":my_host["ip"],
            "hostname":my_host["hostname"],
            "accounts":accounts,
            "ports":ports,
            "date":date
        });
 
# PRINT TABLE HEADERS
print(
    adjust_item("DATE", 16 ),
    adjust_item("IP", 15),
    adjust_item("HOSTNAME", 40),
    adjust_item("ACCOUNTS", 30) + adjust_item("NOFA ", 4),
    adjust_item("PORT RANGE", 12),
    adjust_item("NOFP",5)
)
 
# GENERATING OUTPUT
# DATE             IP              HOSTNAME                                 ACCOUNTS                      NOFA  PORT RANGE   NOFP
# Jun  2 08:47:37  61.174.51.XXX   XXX.51.174.61.dial.XXX.dynamic.163data   root|admin                    2     2804 ->58246 30
 
for item in full_hosts_data:
 
    largest_port, smallest_port, port_count = port_parser(item["ports"])
    five_accounts, account_counter = first_5(item["accounts"])
 
    parsed_ip           = adjust_item( item["ip"],          15 )
    parsed_host         = adjust_item( item["hostname"] ,   40 )
    parsed_accounts     = adjust_item( five_accounts,       30 )
    parsed_acounter     = adjust_item( str(account_counter), 5 )
    parsed_portrange    = adjust_item(str(smallest_port),    5 ) + "->" + adjust_item(str(largest_port) ,5 )
    parsed_port_count   = adjust_item( str(port_count),      5 )
    parsed_date         = adjust_item( item["date"],        16 )
 
    print(
        parsed_date[:16],
        parsed_ip, parsed_host[:40],
        parsed_accounts[1:30],
        parsed_acounter,
        parsed_portrange,
        parsed_port_count
    )