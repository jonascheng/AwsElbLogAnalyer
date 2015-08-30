#!/usr/bin/env python
# 
# The script will look up information from http://whatismyipaddress.com/ip/ against a list of IP
# Please specify a file which contains a list of IP, all the line in each line will be processed 
# and return in csv format.
#
from bs4 import BeautifulSoup
import urllib2
import logging
import random
import time
import sys
import os

BaseURL = "http://whatismyipaddress.com/ip/"
UserAgent = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'
]

class Cache:
    def __init__(self, cacheFile):
        if os.path.isfile(cacheFile) == True:
            self.ipCache = set(self.parseIP(cacheFile))
        else: 
            self.ipCache = set("")

    @classmethod
    def load(cls, cacheFile):
        return cls(cacheFile)

    @classmethod
    def empty(cls):
        return cls("")

    def parseIP(self, cacheFile):
        ipList = []
        with open(cacheFile, "r") as ins:
            for line in ins:
                # Example format
                # 67.8.236.110  1124658286  67-8-236-110.res.bhn.net    33363   Time Warner Cable   Time Warner Cable   None detected   Broadband   Dynamic IP
                #
                ls = line.split("\t")
                try:
                    ipList.append(ls[0].rstrip())
                except:
                    logging.error(ls)
                    continue
        return ipList

    def isIPCached(self, ip):
        if ip in self.ipCache:
            logging.info("hit " + ip)
            return True
        return False

    def addIP(self, ip):
        logging.info("addIP " + ip)
        self.ipCache.add(ip)

def requester(ip):
    url = BaseURL + ip
    try:
        req = urllib2.Request(url)
        req.add_unredirected_header('User-Agent', random.choice(UserAgent))
        return urllib2.urlopen(req).read()
    except urllib2.HTTPError, err:
        logging.error(err)
        raise

def parser(response):
    soup = BeautifulSoup(response)
    ls = []
    for div in soup.findAll("div", {'id': 'section_left_3rd'}):
        for tb in div.findAll("table"):
            for tr in tb.findAll("tr"):
                for td in tr.findAll("td"):
                    if td.string != None:
                        ls.append(td.string)
            break
    return ls

# toggle the logging level
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# collect all access log file(s) into a list
if len(sys.argv) >= 2:
    # initial whatismyipaddress cache
    try:
        print(sys.argv[2])
        cacheFile = sys.argv[2]
        objCache = Cache.load(cacheFile)
    except:
        objCache = Cache.empty()
    file = sys.argv[1]
    ipFailed = []
    with open(file, "r") as ins:
        for ip in ins:
            ip = ip.rstrip()
            logging.info("processing " + ip)
            try:
                if objCache.isIPCached(ip) != True:
                    #response = requester(ip)
                    #attributes = parser(response);
                    #print("\t".join(attributes))
                    # cache the ip
                    objCache.addIP(ip)
                else:
                    continue
            except:
                ipFailed.append(ip)
            # delay to prevent from server blocking the request
            time.sleep(15)
    if len(ipFailed) != 0:
        print("\nThe following IP got exception:\n")
        print("\n".join(ipFailed))
