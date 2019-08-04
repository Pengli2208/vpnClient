#!/usr/bin/env python  
# encoding: utf-8  
""" 
@version: v1.4
@author: Paul Li 
@license: Apache Licence  
@contact: lpy_ren@163.com 
@software: Visual studio 
@file: socketio_t.py 
@time: 2019/8/4 10:31 
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

nfsPath = '/mnt/nfs_py'
versionFile = 'version.txt'
localPath = '/home/pi/vpnClient'
tmpFile = 'updatelog.txt'


def TestSyncFile():

	pathLog = os.path.join(localPath, tmpFile)

	if  False == os.path.exists(nfsPath):
		os.mkdir(nfsPath)
	os.system("sudo mount  -t  nfs      -o  nolock  192.168.0.1:/home/pi/vpnClient  /mnt/nfs_py")
	path1 = os.path.join(nfsPath,versionFile) 
	path2 = os.path.join(localPath, versionFile)
	if False == os.path.exists(path1):
		return




	with open(path1, 'r') as f:
		linesNfs = f.readlines()

	with open(path2, 'r') as f:
		linesLoc = f.readlines()

	verionLoc = 0
	versionNfs = 0 
	if len(linesNfs) >= 2:
		versionNfs = int(linesNfs[0])

	if len(linesLoc) >= 2:
		versionLoc = int(linesLoc[0])

	if versionNfs > versionLoc:
		starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		with open(pathLog, 'a+') as f:
			f.write('update  again'+starttime)
		cpCmd = 'sudo cp -rf {} {}'.format(nfsPath, localPath)
		os.system(cpCmd)
		print(cpCmd)
		cpCmd = 'sudo cp -rf {} {}'.format(localPath+'/nfs_py/*', localPath)
		os.system(cpCmd)
		print(cpCmd)
		with open(pathLog, 'a+') as f:
			f.write('update finish \n')
		with open(path2, 'r') as f:
			linesLoc = f.readlines()
	
		if len(linesLoc) >= 2:
			shCmd = linesLoc[1]
	
			if shCmd.find('.sh') != -1:
				shCmd = os.path.join(localPath, shCmd)
				print(shCmd)
				os.system(shCmd) 
	else:
		print('same version, no need to sync')


	


if __name__ == '__main__':
	while True:
		time.sleep(10)
		TestSyncFile()


