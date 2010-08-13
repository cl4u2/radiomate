#!/usr/bin/env python
# vim:fileencoding=utf-8:nomodified

from distutils.core import setup

setup(
				name='radiomate',
				version='0.1',
				description='Radio Automation Made Easy',
				author='Claudio Pisa',
				author_email='clauz aat ninux dot org',
				url='http://radiomate.org',
				license='GPL',
				packages=[
						'radiomate', 
						'radiomate.jukeslots' 
						],
				requires=[
						'MySQLdb'
						],
				data_files=[
						('', [
								'README', 
								'INSTALL', 
								'TODO', 
								'COPYING', 
								'JsonAPI.txt', 
								'radiomate0.sql', 
								'radiomated.py', 
								'radiomatejson.cgi'
								]),
						('tests', [
								'cgitest.html',
								'daotest.py',
								'json.js',
								'jsontest.py',
								'tmp.py'
								])
						]
				)


