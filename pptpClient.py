#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# @File  :
# @Author: Paul Li
# @Date  : 2019/1/3
# @Desc  :

import socket
import select
import base64
import time
from multiprocessing import Process, Lock
from os import system
#import traceback
import os, sys, socket, struct, select, time
import shutil
import sys
import string 
import psutil
import re
import uuid
import fcntl
from subprocess import Popen, PIPE

#socket try connect
import os,signal


#ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.
#socket.setdefaulttimeout(4)

#first argument
#host=sys.argv[1]

#second argument
#port=int(sys.argv[2])

def RestartVPN():
    #out=os.popen("ps aux | grep pptp").read()

    #for line in out.splitlines():
    #    print(line)
    #    if 'pptpconf' in line:
    #        pid = int(line.split()[1])
    #        print(pid)
    #        os.kill(pid, signal.SIGKILL)
    #        print('已杀死pid为%s的进程,　返回值是:%s' % (pid, a))
    #time.sleep(10)
    os.system('sudo poff pptpconf')
    time.sleep(3)
    os.system('sudo pon pptpconf')
    #time.sleep(10)



def PortOpen(ip, port):
    print( '\033[1m*Port\033[0m %s:%d' %(ip,port)),
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        s.connect((ip,port))
        s.shutdown(2)
        print( '\033[1;32m.... is OK.\033[0m' )
        return True

    except socket.timeout:
        print( '\033[1;33m.... is down or network time out!!!\033[0m' )
        return False

    except:

        print( '\033[1;31m.... is down!!!\033[0m' )
        return False

def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = ord(source_string[count + 1]) * 256 + ord(
            source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff  # Necessary?
        count = count + 2
    if countTo < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff  # Necessary?
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return
        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
          "bbHHh", icmpHeader)

        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return

def send_one_ping(my_socket, dest_addr, ID):
    """
  Send one ping to the given >dest_addr<.
  """
    dest_addr = socket.gethostbyname(dest_addr)
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0
    # Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    #a1 = struct.unpack("bbHHh",header)  #my test
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data
    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)
    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1)
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1
def do_one(dest_addr, timeout):
    """
  Returns either the delay (in seconds) or none on timeout.
  """
    delay=None
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        my_ID = os.getpid() & 0xFFFF
        send_one_ping(my_socket, dest_addr, my_ID)
        delay = receive_one_ping(my_socket, my_ID, timeout)
        my_socket.close()
    except socket.error:
        if errno == 1:
            # Operation not permitted
            msg = msg + (
              " - not root."
            )
            raise socket.error(msg)
        #raise # raise the original error
    except Exception as e:
        print(e)
    return delay
def verbose_ping(dest_addr, timeout = 2, count = 4):
    """
  Send >count< ping to >dest_addr< with the given >timeout< and display
  the result.
  """
    ret = 0
    for i in xrange(count):
        print( "\033[1m*Ping\033[0m %s ..." % dest_addr)
        try:
            delay = do_one(dest_addr, timeout)
        except Exception as e:
            print( "\033[1;31m... failed. (%s)" % e)
            break
        if delay == None:
            print("\033[1;31m... failed. (timeout within %ssec.)\033[0m" % timeout)
        else:
            delay = delay * 1000
            print("\033[1;32m... get ping in %0.4fms\033[0m" % delay)
            ret = ret+1
    return ret


def get_user_name():
    filename = '/home/pi/clientName'
    if os.path.exists(filename):
        name = open(filename,'r').read()
        name = name.split('\n')
        return name[0]
    return 'unknown'


def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    #return mac



def getIfconfig():
    p = Popen(['ifconfig'], stdout = PIPE)
    stdout1 = p.stdout.read()
    stdout1 = str(stdout1,'utf-8')
    data = stdout1.split('\n\n')
    return [i for i in data if i and not i.startswith('lo')]

def parseIfconfig(data):
    dic = {}
    #print(len(data),data)
    for devs in data:
        lines = devs.split('\n')
        #print(len(lines),lines)
        #print('\n\n\n')
        devname = lines[0].split()[0]
        #macaddr = lines[0].split()[-1]
        #ipaddr  = lines[1].split()[1].split(':')[1]
        ipaddr  = lines[1].split()[1]#[1].split(':')[1]
        #print('ipadr,', ipaddr)
        dic[devname] = ipaddr #[ipaddr, macaddr]
    return dic

def get_ip_address(devname):
    ip = '00.00.00.00'
    data = getIfconfig()
    dict1 = parseIfconfig(data)
    print(dict1)
    devname += ':'
    ip1 = dict1.get(devname, ip)
    return ip1     



def get_user_name1():
    path = os.getcwd()
    for root, dirs, files in os.walk(path):  # path 为根目录
        fileexd = os.path.splitext(files)
        if fileexd[1] =='.ovpn':
            return fileexd[0]
    return 'unknown'


def RegOnline(port1, _type):
    ret = 0
    host = "192.168.0.1"
    user = 'unknown'
    mac = '00:00:00:00:00:00'
    ip = '0.0.0.0'

    try:
        mac = get_mac_address()
    except Exception as e:
        print('error', repr(e))
        pass

    try:
        user = get_user_name()
    except Exception as e:
        print('error', repr(e))
        pass

    try:
        ip = get_ip_address('ppp0')
    except Exception as e:
        print('error', repr(e))
        pass

    sqlMsg = "{},{},{},{},".format(_type, mac, user, ip)
    sendStr = "register_vpn<>" + str(sqlMsg)
    print('send str,', sendStr)
    writeLog('send str,' + sendStr)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port1))
        client.send(sendStr.encode('utf8'))
        client.close()
        writeLog("Socket Send finished")
        ret = 1
    except Exception as e:
        writeLog("server is not reached")
        print("server is not reached")
        pass

    return ret

#print(get_mac_address())
#print(get_user_name())
def writeLog(data):
    tmpFile  = '/home/pi/tmplog.conf'
    with open(tmpFile, 'a+') as f:
        f.write(data)
        f.write('\n')

if __name__ == "__main__":
    port = 1795
    tmpFile  = '/home/pi/tmp.conf'
    writeLog('pptpClient started')
    time.sleep(30)
    writeLog('sleep 30')
    RegOnline(port, 0)
    serverErrCnt = 0
    dnsUpdate = 0
    append1 = 'nameserver 114.114.114.114'
    append2 = 'nameserver 8.8.8.8'
    while True:
        time.sleep(90)
        ret = RegOnline(port, 1)
        if ret == 0:
            serverErrCnt = serverErrCnt + 1
        else:
            serverErrCnt = 0
#        ret = PortOpen('baidu.com', 80)
        ret = True
        if ret == False:
            sourceFile = '/etc/resolv.conf'
            tmpFile  = '/home/pi/tmp.conf'
            open(tmpFile, "wb").write(open(sourceFile, "rb").read())

            open(sourceFile, "wb").writelines(append1)
            open(sourceFile, "a+").writelines(append2)
            open(sourceFile, "a+").write(open(tmpFile, "rb").read())
            dnsUpdate = dnsUpdate + 1
            print('ping baidu failed,',dnsUpdate)
        else:
            dnsUpdate = 0

        if dnsUpdate > 10:
            # no internet connection; need to restart device
            print('sudo reboot,', dnsUpdate)
            os.system('sudo reboot')
            dnsUpdate = 0

            # ping ok;
        if serverErrCnt > 5:
            serverErrCnt = 0
            # reset vpn connection
            print('openvpn reset')
            RestartVPN()
            dnsUpdate = 0

