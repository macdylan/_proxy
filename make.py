#!/usr/bin/env python

import os
import urllib2
import time
import ipcalc

PROXY_ADDR = '127.0.0.1:11090'

curdir =  os.path.abspath(os.path.dirname(__file__))

url = r'http://ftp.apnic.net/apnic/dbase/data/country-ipv4.lst'

pacfile = open(os.path.join(curdir, 'auto.pac'), 'w')
pacfile.write('''/* Last update: %(time)s */
function FindProxyForURL(url, host) {
    if (isPlainHostName(host)) return "DIRECT";
    var proxies = "SOCKS5 %(addr)s; SOCKS %(addr)s; DIRECT";
''' % {'time': time.asctime(), 'addr': PROXY_ADDR})

try:
    gfwfile = open(os.path.join(curdir, 'gfw.list'), 'r')
    for line in gfwfile.readlines():
        pacfile.write('''    if (dnsDomainIs(host, "%s")) return proxies;\n''' % line.strip())
    gfwfile.close()
except IOError:
    pass

pacfile.write('''
    var resolved_ip = dnsResolve(host);
    if (isInNet(resolved_ip, "10.0.0.0", "255.0.0.0")
        || isInNet(resolved_ip, "172.16.0.0", "255.240.0.0")
        || isInNet(resolved_ip, "192.168.0.0", "255.255.0.0")
        || isInNet(resolved_ip, "127.0.0.0", "255.255.255.0"))
        return "DIRECT";
    // "cn" net ...
''')

req = urllib2.Request(url)
handler = urllib2.urlopen(req)
remote_etag = handler.headers.getheader('etag')

etagfile = os.path.join(curdir, 'apnic.etag')
try:
    etag = open(etagfile, 'r').readline().strip()
except IOError:
    etag = None

if remote_etag != etag:
    print "Remote E-Tag has changed! requesting to download."
    lines = handler.readlines()
    etagh = open(etagfile, 'w')
    etagh.write(remote_etag + '\n')
    etagh.write(''.join(lines))
    etagh.close()
    print "Downloaded."
else:
    # The first line is E-Tag value
    lines = open(etagfile, 'r').readlines()[1:]

for line in lines:
    if line.find(': cn ') < 0:
        continue
    # r = line.split(':')[0]
    # f, t = map(lambda x:x.strip(), r.split('-'))
    # pacfile.write('''    if(isInNet(resolved_ip, "%s", "%s")) return "DIRECT";\n''' % (f, t))
    r = line.split(':')[1]
    ip, sub = r.strip().split('/')
    ip = ip + '.0' * (4 - len(ip.split('.'))) # 180.0 -> 180.0.0.0
    ipr = '/'.join([ip, sub]) # 180.0/20 -> 180.0.0.0/20
    pacfile.write('''    if(isInNet(resolved_ip, "%s", "%s")) return "DIRECT";\n''' % (ip, ipcalc.Network(ipr).netmask().dq))

pacfile.write('''
    return proxies;
}''')
pacfile.close()
