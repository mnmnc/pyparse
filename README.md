# PyParse

A simple authentication log parser written in Python3.

### Required modules
* re
* colorama
* socket

###

This simple script is just an exercise. I’m learning Python and frankly i just like to parse text files.

Code below will parse the /var/log/auth.log file and search for failed authentication attempts. For each failed attempt it will record IP address, date, account used to authenticate and remote port used to authenticate. It will then resolve the IP to hostname, generate list of distinct accounts and ports used by particular IP address. This list will be displayed at the end of script execution. Instead of showing all ports used it shows just the range from the lowest to highest. By default only first five accounts are displayed in the table (unless list of those five is longer than 30 chars – in such case the list is truncated). If you would want to display all accounts recorded you can replace the code in line 176 from this one:

`parsed_accounts     = adjust_item( five_accounts,         30 )`

to this one:
	
`parsed_accounts     = item["accounts"]`

The columns NOFA and NOFP are showing number of accounts and number of ports used respectively. The date showed can be read as ‘last seen’ for particular IP address.

The example output:
