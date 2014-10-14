#!/usr/bin/python
# -*- coding: utf-8 -*-

import engine
import os
import shutil
import sys
import argparse


if not os.path.isfile('config.py'):
	shutil.copyfile('config_empty.py', 'config.py')

import config
if config.TWITTER_CONSUMER_KEY == '' or config.TWITTER_CONSUMER_SECRET == '' or config.TWITTER_ACCESS_TOKEN == '' or config.TWITTER_TOKEN_SECRET == '':
	print 'please fill all the KEYs and TOKENs in config.py'
	exit(666)


#parser = argparse.ArgumentParser(description='check your twitter account for the unfollow-bug')
#parser.add_argument('--operation', metavar='-op', type=str,
#					default='check',
#					help='select Operation: check/mark (default: check)')

#parser.add_argument('--iUnfollowd', type=str,
#					default='',
#					help='select Operation: check/mark (default: check)')

#parser.add_argument('--sum', dest='accumulate', action='store_const',
#					const=sum, default=max,
#					help='sum the integers (default: find the max)')

#args = parser.parse_args()


mode = 'check'
subMode = ''
for arg in sys.argv:
	if '-h' in arg or '--help' in arg:
		print 'by default this program does not need parameters for the check'
		print ''
		print 'IF there are "missing" following accounts and you have unfollowed them by yourself, use:'
		print 'start.py --mode=mark iRemoved'
		print 'they will be tagged as "removed by me" and wont show up again.'
		exit()
	if '--mode=' in arg:
		mode = arg.replace('--mode=', '')
	if arg == 'iRemoved':
		subMode = 'iRemoved'

if mode == 'check':
	eng = engine.engine()
	eng.doCheck()
elif mode == 'mark':
	if subMode == '':
		print 'please set "iRemoved" to mark ALL lost followed as "removed by you"!'
	elif subMode == 'iRemoved':
		eng = engine.engine()
		eng.setMarkAs(1)