#!/usr/bin/python
#
# Andrew Clayton <andrew@pccl.info>
#
# Based on code from: http://docs.python.org/lib/node161.html
#

import os, sys, email, errno, mimetypes, string
from time import time
from datetime import datetime


def create_directories():
	global year, month, day, whoami, maildir

	try:
		os.mkdir(maildir+"/"+whoami)
	except OSError, e:
		if e.errno <> errno.EEXIST:
			raise

	try:
		os.mkdir(maildir+"/"+whoami+"/"+year)
	except OSError, e:
		if e.errno <> errno.EEXIST:
			raise

	try:
		os.mkdir(maildir+"/"+whoami+"/"+year+"/"+month)
	except OSError, e:
		if e.errno <> errno.EEXIST:
			raise

	try:
		os.mkdir(maildir+"/"+whoami+"/"+year+"/"+month+"/"+day)
	except OSError, e:
		if e.errno <> errno.EEXIST:
			raise


t       = datetime.now()
year    = t.strftime("%Y")
month   = t.strftime("%m")
day     = t.strftime("%d")
ts      = t.strftime("%s")

# Find out who we where called as
whoami     = string.split(os.path.basename(sys.argv[0]), ".")[0]

# Either save data to system directory or in user specified directory
# Change maildir accordingly
if len(sys.argv) == 1:
	maildir    = "/tmp/maildata"
	output_dir = maildir+"/"+whoami+"/"+year+"/"+month+"/"+day
	create_directories()
else:
	output_dir = sys.argv[1]

# Get and save message
lines = sys.stdin.readlines()
ofp = open(output_dir+"/maildata-"+ts+".dat", "w")
for line in lines:
	ofp.write(line)

ofp.close()

# Read in saved message
ofp = open(output_dir+"/maildata-"+ts+".dat", "r")
msg = email.message_from_file(ofp)
ofp.close()

counter = 0
for part in msg.walk():
	# multipart/* are just containers
	if part.get_content_maintype() == 'multipart':
		continue

	ext = mimetypes.guess_extension(part.get_content_type())
	if not ext:
		# Use a generic bag-of-bits extension
		ext = '.bin'
	
	filename = 'part-%03d%s' % (counter, ext)
	
	counter += 1
	fp = open(output_dir+"/"+filename, 'wb')
	fp.write(part.get_payload(decode = True))
	fp.close()

