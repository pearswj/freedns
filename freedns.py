#!/usr/bin/python2
""" 
 Quick Linux DNS IP Updater Python script for FreeDNS (freedns.afraid.org)
 
 Author: Daniel Gibbs
 Version: 0.2
 URL: http://www.danielgibbs.net/
 
 ** Must set update_key and make sure that ip_file is read and writable
 
 This program is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License as published by the Free Software
 Foundation; either version 2 of the License, or (at your option) any later
 version.
 
 This program is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 
 """
import sys
import os
import time
import stat
from urllib2 import urlopen
from urllib2 import URLError, HTTPError
import logging
import argparse

# Parse Args
parser = argparse.ArgumentParser(description='Update Afraid.org dynamic dns.')
parser.add_argument('-q', dest='consolelevel', action='store_const',
                   const=logging.ERROR, default=logging.INFO,
                   help='only show errors in the console')
parser.add_argument('-f', dest='logfile', action='store',
                   default='.freedns_log',
                   help='file to log output to')
args = parser.parse_args()

# Create Logger
log = logging.getLogger('freedns')
logging.basicConfig(format='%(levelname)-8s [%(asctime)s] %(name)s: %(message)s',
                   level=logging.INFO, stream=sys.stdout,
                   filename=args.logfile, filemode='a')
console = logging.StreamHandler()
console.setLevel(args.consolelevel)
logging.getLogger('').addHandler(console)
 
# FreeDNS Update Key
update_key = "UPDATE_KEY_HASH"
 
# FreeDNS Update URL
update_url = "http://freedns.afraid.org/dynamic/update.php?" + update_key
 
# External IP URL (must return an IP in plain text)
ip_urls = ("http://www.dangibbs.co.uk/ip.php","http://automation.whatismyip.com/n09230945.asp")
 
# Attempt to open URL to return the external IP
for ip_url in ip_urls:
    try:
        external_ip = urlopen(ip_url).read()
        break
    except URLError as e:
        log.info("Couldn\'t retrieve external IP from " + str(ip_url) + " (" + str(e) + ")")
        external_ip = None

if not external_ip:
    log.error("No external IP found (see the log). Exiting...")
    log.info("Check your internet connection and/or the list of IP URLs (see freedns.py)")
    sys.exit()

# The file where the last known external IP is written
ip_file = ".freedns_ip"
 
# Create the file if it doesnt exist otherwise update old IP
if not os.path.exists(ip_file):
    fh = open(ip_file, "w")
    fh.write(external_ip)
    fh.close()
    last_external_ip = "Unknown"
    log.info("Created FreeDNS IP log file: " + ip_file)
else:
    fh = open(ip_file, "r")
    last_external_ip = fh.read()
    last_external_ip = last_external_ip.rstrip('\n')
 
# Check old IP against current IP and update if necessary
if last_external_ip != external_ip:
    urlopen(update_url)
    log.info("External IP updated FROM (" + last_external_ip + ") TO (" + external_ip + ")")
    fh = open(ip_file, "w")
    fh.write(external_ip)
    fh.close()
else:
    last_ip_update = time.ctime(os.stat(ip_file).st_mtime)
    log.info("External IP (" + external_ip + ") has not changed.")
    log.info("Last update was " + last_ip_update)
