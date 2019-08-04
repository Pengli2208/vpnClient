#!/usr/bin/env python  
# encoding: utf-8  
""" 
@version: v1.0 
@author: Paul Li 
@license: Apache Licence  
@contact: lpy_ren@163.com 
@software: Visual studio 
@file: socketio_t.py 
@time: 2019/6/27 10:31 
@describe: 采用 socketio 模块进行消息发布与接收
"""
import sys
import os
import socketio
import socket
import sys
import threading
import time
import os
import datetime

from multiprocessing import Process


import socket
import fcntl
import struct

import socket
import fcntl
import struct
import uuid


sio = socketio.Client()
name_space = '/test'

def get_user_name():
    path = os.getcwd()
    for root, dirs, files in os.walk(path):  # path 为根目录
        fileexd = os.path.splitext(files)
        if fileexd[1] =='.ovpn':
            return fileexd[0]
    return 'unknown'

def get_mac_address():
    node = uuid.getnode()
    mac = uuid.UUID(int = node).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
    #return mac


  
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifname = bytes(ifname.encode('utf-8'))
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])


#print(get_ip_address('lo'))
#print(get_ip_address('eth0'))
#print(get_mac_address())



def ThreadConn():
    global sio
    user = 'test1'
    mac = '00:00:00:00:00:00'
    ip = '0.0.0.0'

    starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #mac text,user text, ip text,starttime text, refreshtime text
    while True:		
        try:		
            sio.connect('http://procontrol.top:5000/')
            print('connect ok')
            sio.sleep(5)
            try:
                mac = get_mac_address()
            except Exception as e:
                print('error', repr(e))
                pass   

            try:
                ip = get_ip_address('tun0')
            except Exception as e:
                print('error', repr(e))
                pass
            refreshtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data = "{},{},{},{},{}".format(mac,user, ip,starttime,refreshtime)
            print('emit, and refresh',data)
            sio.emit('my_reg_connection', {'room': user, 'data': data, 'response':'add new user'}, namespace=name_space)
            sio.sleep(5)
            sio.disconnect()
            sio.sleep(60)
        except Exception as e:
            print('error', repr(e))
            pass

if __name__ == '__main__':
    
    tlist = []  # 线程列表，最终存放两个线程对象
    p = threading.Thread(target=ThreadConn, args=())
    tlist.append(p)
    for t in tlist:
        t.start()
    for t in tlist:
        t.join()