#!/usr/bin/python
#
# recmail.py - A program to receive and store email attachments
#
# Based on code from: http://docs.python.org/lib/node161.html
#
# Copyright (c) 2008-2010	Andrew Clayton <andrew@pccl.info>
# Released under the GNU General Public License (GPL) version 2.
# See COPYING
#

import os, sys, email, errno, mimetypes, string, uuid
from time import time
from datetime import datetime


def create_directories(output_dir):
	global year, month, day, whoami, maildir

	try:
		os.makedirs(output_dir)
	except OSError, e:
		if e.errno <> errno.EEXIST:
			raise

 	# While loop should be superflous as uuid4() should always be unique
	while True:
		try:
			myuuid = uuid.uuid4()
			os.mkdir(output_dir+"/"+str(myuuid))
			return output_dir+"/"+str(myuuid)
		except OSError, e:
			if e.errno == errno.EEXIST:
				continue


os.umask(0007)

t       = datetime.now()
year    = t.strftime("%Y")
month   = t.strftime("%m")
day     = t.strftime("%d")

# Find out who we were called as
whoami  = string.split(os.path.basename(sys.argv[0]), ".")[0]

# Either save data to system directory or in user specified directory
# Change maildir accordingly
if len(sys.argv) == 1:
	maildir    = "/data/maildata"
	output_dir = maildir+"/"+whoami+"/"+year+"/"+month+"/"+day
	output_dir = create_directories(output_dir)
else:
	output_dir = sys.argv[1]

# Get and save message
lines = sys.stdin.readlines()
ofp = open(output_dir+"/maildata.dat", "w")
for line in lines:
	ofp.write(line)

ofp.close()

# Read in saved message
ofp = open(output_dir+"/maildata.dat", "r")
msg = email.message_from_file(ofp)
ofp.close()

counter = 0
ifp = open(output_dir+"/00INDEX", "w")
for part in msg.walk():
	# multipart/* are just containers
	if part.get_content_maintype() == 'multipart':
		continue

	ext = mimetypes.guess_extension(part.get_content_type())
	if not ext:
		# Use a generic bag-of-bits extension
		ext = '.bin'
	
	if ext == '.dot':
		# Python has two entries for application/msword, rename .dot to .doc
		ext = '.doc'

	filename = 'part-%03d%s' % (counter, ext)

	# Write attached filename and stored filename to INDEX file
	ifp.write(filename+"\t"+str(part.get_filename())+"\n")

	counter += 1
	fp = open(output_dir+"/"+filename, 'wb')
	fp.write(part.get_payload(decode = True))
	fp.close()

ifp.close()
