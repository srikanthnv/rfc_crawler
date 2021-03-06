#!/usr/bin/env python

#Scan through arguments: need the 'max' RFC number, and a dir location to
#archive downloaded files. The archive will be checked before downloading
#a new RFC. The resulting graph will be stored as JSON.

import os.path
import urllib
import time
from bs4 import BeautifulSoup
import re
import json
import signal
import sys
import argparse
#from guppy import hpy
import shelve

#h = hpy()
parser = argparse.ArgumentParser(description='RFC crawler')
parser.add_argument('maxrfc', metavar='MAX', type=int,
				     help='The max RFC number to crawl')
parser.add_argument('archdir', metavar='ARCHDIR', type=str,
				     help='Location to archive downloaded RFCs')
parser.add_argument('outfile', metavar='OUTFILE', type=str,
				     help='JSON file to output')

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
	if os.path.exists(rfcpath):
		print 'RFC'+str(rfc)+' already exists, skipping download'
		return
	print 'Downloading RFC'+str(rfc)
	urllib.urlretrieve(rfcurl, rfcpath)
#	time.sleep(5)
#--
#--

#--
#Function parses through an RFC and returns RFC title and a list of RFCs that it references
#--
def parse_rfc(rfc):
	refs = set()
	rfcpath = args.archdir+'/rfc'+str(rfc)+'.html'
	soup = BeautifulSoup(open(rfcpath, 'r').read())
	if not soup.title:
		return ["Does not exist", set([])]
	print soup.title
	rfc_re_obj = re.compile('\.\/rfc([0-9]+)', re.IGNORECASE)
	for link in soup.find_all('a'):
		href = link.get('href')
		if href:
			m = rfc_re_obj.match(href)
			if m and m.group(1) != str(rfc):
				refs.add(int(m.group(1)))
				#print m.group(1)
	title = soup.title.string
	del soup
	return [title, refs]

pending_rfc_set = set(range(1,args.maxrfc + 1))
crawled_rfc_set = set()
#graph = shelve.open('rfcgraph', 'n')
graph = { }

class SetEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)
		return json.JSONEncoder.default(self, obj)
def rfcexit():
	print 'Writing graph to file...'
	f = open(args.outfile, 'w')
	json.dump(graph, f, cls=SetEncoder, sort_keys=True,
		indent=4, separators=(',', ': '));
	f.close();

def signal_handler(signal, frame):
	rfcexit()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

#Crawl through the RFCs and build graph
while(pending_rfc_set):
	print '\n\n'
	print 'PENDING = '+str(len(pending_rfc_set))+ ' RFCs '
	rfc = pending_rfc_set.pop()
	if not rfc in crawled_rfc_set:
		check_get_rfc(rfc)
		[title, refs] = parse_rfc(rfc)
		crawled_rfc_set.add(rfc)

		srfc = str(rfc)
		graph[srfc]={}
		graph[srfc]["title"] = title;
		graph[srfc]["refs"] = refs;

		#before = len(refs)
		#refs -= crawled_rfc_set
		#after = len(refs)
		#print '>>Eliminated ' + str(before - after) + ' duplicates, ' + str(len(refs)) + ' new RFCs added'
		#pending_rfc_set |= refs
		#print h.heap();
rfcexit();
