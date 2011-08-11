#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified
#
#  Copyright 2010 Claudio Pisa (clauz at ninux dot org)
#
#  This file is part of RadioMate
#
#  RadioMate is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  RadioMate is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with RadioMate.  If not, see <http://www.gnu.org/licenses/>.
#

import cgitb
cgitb.enable()

import cgi
import radiomate.jsonif
from radiomate.config import MEDIAFILESHOMEDIR
import sys
import os
import time

FILEUPLOADKEY = 'upload'

def isMp3Valid(file_path):
		"thanks to Peter Carroll http://blog.eringal.com/python/verifying-that-an-mp3-file-is-valid-in-python/"
		is_valid = False

		f = open(file_path, 'r')
		block = f.read(1024)
		frame_start = block.find(chr(255))
		block_count = 0 #abort after 64k
		while len(block)>0 and frame_start == -1 and block_count<64:
				block = f.read(1024)
				frame_start = block.find(chr(255))
				block_count+=1
		   
		if frame_start > -1:
				frame_hdr = block[frame_start:frame_start+4]
				is_valid = frame_hdr[0] == chr(255)
		   
				mpeg_version = ''
				layer_desc = ''
				uses_crc = False
				bitrate = 0
				sample_rate = 0
				padding = False
				frame_length = 0
		   
				if is_valid:
						is_valid = ord(frame_hdr[1]) & 0xe0 == 0xe0 #validate the rest of the frame_sync bits exist
				   
				if is_valid:
						if ord(frame_hdr[1]) & 0x18 == 0:
								mpeg_version = '2.5'
						elif ord(frame_hdr[1]) & 0x18 == 0x10:
								mpeg_version = '2'
						elif ord(frame_hdr[1]) & 0x18 == 0x18:
								mpeg_version = '1'
						else:
								is_valid = False
				   
				if is_valid:
						if ord(frame_hdr[1]) & 6 == 2:
								layer_desc = 'Layer III'
						elif ord(frame_hdr[1]) & 6 == 4:
								layer_desc = 'Layer II'
						elif ord(frame_hdr[1]) & 6 == 6:
								layer_desc = 'Layer I'
						else:
								is_valid = False
		   
				if is_valid:
						uses_crc = ord(frame_hdr[1]) & 1 == 0
				   
						bitrate_chart = [
								[0,0,0,0,0],
								[32,32,32,32,8],
								[64,48,40,48,16],
								[96,56,48,56,24],
								[128,64,56,64,32],
								[160,80,64,80,40],
								[192,96,80,96,40],
								[224,112,96,112,56],
								[256,128,112,128,64],
								[288,160,128,144,80],
								[320,192,160,160,96],
								[352,224,192,176,112],
								[384,256,224,192,128],
								[416,320,256,224,144],
								[448,384,320,256,160]]
						bitrate_index = ord(frame_hdr[2]) >> 4
						if bitrate_index==15:
								is_valid=False
						else:
								bitrate_col = 0
								if mpeg_version == '1':
										if layer_desc == 'Layer I':
												bitrate_col = 0
										elif layer_desc == 'Layer II':
												bitrate_col = 1
										else:
												bitrate_col = 2
								else:
										if layer_desc == 'Layer I':
												bitrate_col = 3
										else:
												bitrate_col = 4
								bitrate = bitrate_chart[bitrate_index][bitrate_col]
								is_valid = bitrate > 0
		   
				if is_valid:
						sample_rate_chart = [
								[44100, 22050, 11025],
								[48000, 24000, 12000],
								[32000, 16000, 8000]]
						sample_rate_index = (ord(frame_hdr[2]) & 0xc) >> 2
						if sample_rate_index != 3:
								sample_rate_col = 0
								if mpeg_version == '1':
										sample_rate_col = 0
								elif mpeg_version == '2':
										sample_rate_col = 1
								else:
										sample_rate_col = 2
								sample_rate = sample_rate_chart[sample_rate_index][sample_rate_col]
						else:
								is_valid = False
		   
				if is_valid:
						padding = ord(frame_hdr[2]) & 1 == 1
				   
						padding_length = 0
						if layer_desc == 'Layer I':
								if padding:
										padding_length = 4
								frame_length = (12 * bitrate * 1000 / sample_rate + padding_length) * 4
						else:
								if padding:
										padding_length = 1
								frame_length = 144 * bitrate * 1000 / sample_rate + padding_length
						is_valid = frame_length > 0
				   
						# Verify the next frame
						if(frame_start + frame_length < len(block)):
								is_valid = block[frame_start + frame_length] == chr(255)
						else:
								offset = (frame_start + frame_length) - len(block)
								block = f.read(1024)
								if len(block) > offset:
										is_valid = block[offset] == chr(255)
								else:
										is_valid = False
		   
		f.close()
		return is_valid

print "Content-type: text/plain;charset=utf-8"
print 

req = None
fs = cgi.FieldStorage()
try:
		rk = fs.keys()[0]
		if rk == FILEUPLOADKEY:
				fileitem = fs[FILEUPLOADKEY]	
				bfn = os.path.basename(fileitem.filename)
				longpath = MEDIAFILESHOMEDIR + "/" + bfn 
				if os.path.exists(longpath):
						longpath = MEDIAFILESHOMEDIR + "/" + str(time.time()).split('.')[0] + "+" +  bfn 
				if os.path.exists(longpath):
						resp = '{"requested": "upload", "warning": "file already exists", "description": "file not uploaded", "responsen": 202, "response": "alreadyexists", "path": "%s"}' % longpath
				else:
						f = open(longpath, 'wb', 10000)
						while True:
								chunk = fileitem.file.read(10000)
								if not chunk: break
								f.write(chunk)
						f.close()
						if isMp3Valid(longpath):
								resp = '{"requested": "upload", "warning": null, "description": "file uploaded", "responsen": 0, "response": "ok", "path": "%s"}' % longpath
						else:
								resp = '{"requested": "upload", "warning": "file is not a valid mp3", "description": "file uploaded", "responsen": 0, "response": "ok", "path": "%s"}' % longpath
		else:
				req = fs.getfirst(rk, "no request")
except:
		raise
		req = "no request"

if req:
		jp = radiomate.jsonif.JSONProcessor()
		resp = jp.process(req)

print resp

