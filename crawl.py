#!/usr/bin/env python

#Scan through arguments: need an RFC to start from, and a dir location to
#archive downloaded files. The archive will be checked before downloading
#a new RFC
import argparse
parser = argparse.ArgumentParser(description='RFC crawler')
parser.add_argument('start', metavar='START', type=int,
				     help='An RFC to start crawling')
parser.add_argument('archdir', metavar='ARCHDIR', type=str,
				     help='Location to archive downloaded RFCs')

args = parser.parse_args()
print args

#--
#Function checks if an RFC exists in the archive, or download it if it doesn't
#--
def check_get_rfc(rfc):
	rfcurl='http://tools.ietf.org/html/rfc'+str(rfc)
	rfcpath=args.archdir+'/rfc'+str(rfc)+'.html'
	print rfcurl
	print rfcpath
	import os.path
	if os.path.exists(rfcpath):
		print 'RFC'+str(rfc)+' already exists, skipping download'
		return
	print 'Downloading RFC'+str(rfc)
	import urllib
	urllib.urlretrieve(rfcurl, rfcpath)
	import time
	time.sleep(5)
#--
#--

#--
#Function parses through an RFC and returns a list of RFCs that it references
#--
def parse_rfc(rfc):
	refs = set()
	rfcpath = args.archdir+'/rfc'+str(rfc)+'.html'
	from bs4 import BeautifulSoup
	soup = BeautifulSoup(open(rfcpath, 'r').read())
	print soup.title
	import re
	rfc_re_obj = re.compile('\.\/rfc([0-9]+)', re.IGNORECASE)
	for link in soup.find_all('a'):
		href = link.get('href')
		if href:
			m = rfc_re_obj.match(href)
			if m and m.group(1) != str(rfc):
				refs.add(int(m.group(1)))
				#print m.group(1)
	return refs

pending_rfc_set = set([args.start])
crawled_rfc_set = set()

while(pending_rfc_set):
	print '\n\n'
	print 'PENDING = '+str(len(pending_rfc_set))+ ' RFCs '
	rfc = pending_rfc_set.pop()
	if not rfc in crawled_rfc_set:
		check_get_rfc(rfc)
		refs = parse_rfc(rfc)
		crawled_rfc_set.add(rfc)
		before = len(refs)
		refs -= crawled_rfc_set
		after = len(refs)
		print '>>Eliminated ' + str(before - after) + ' duplicates, ' + str(len(refs)) + ' new RFCs added'
		pending_rfc_set |= refs

