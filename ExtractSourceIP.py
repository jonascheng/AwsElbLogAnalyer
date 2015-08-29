#!/usr/bin/env python
# 
# The script will extract unique source IP from AWS ELB access log file(s).
# Please specify a folder which contains AWS ELB access log file(s),
# all the file(s) in the folder will be processed and return a list of unique source IP.
#
# Example format:
# 2015-08-27T23:00:02.396604Z tellus-prod-st-ELB-NCU9VB55UWN3 150.70.184.35:47277 
# 172.31.18.86:80 0.000054 0.008674 0.000048 302 302 0 361 "GET https://reporting.
# trendmicro.com:443/bby/report HTTP/1.1" "Mozilla/5.0 (compatible; MSIE 10.0; Win
# dows NT 6.1; Trident/6.0) casperjs e2e check" ECDHE-RSA-AES128-SHA TLSv1
#
import sys
import os

# parse source IP from single ELB access log file
def parseSourceIP(ELBLogfile):
    ipList = []
    with open(ELBLogfile, "r") as ins:
        for line in ins:
            ls = line.split(" ")
            # The format shoudl be IP:PORT
            try:
                sourceIP = ls[2].split(":")
                ipList.append(sourceIP[0])
            except:
                continue
    # remove duplication
    ipList = list(set(ipList))
    return ipList

# collect all access log file(s) into a list
if len(sys.argv) >= 2:
    folder = sys.argv[1]
    fileList = []
    for (dirpath, dirnames, filenames) in os.walk(folder):
        for f in filenames:
            fileList.append(os.path.join(dirpath, f))

ipList = []
for f in fileList:
    ipList.extend(parseSourceIP(f))

# remove dupliction
ipList = list(set(ipList))

# return
print("\n".join(ipList))
