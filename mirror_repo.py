#!/usr/bin/python
import os
import requests
import json
from collections import OrderedDict

ppa_list = [
  ["so-14-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/trusty/main/binary-amd64/Packages"],
  ["so-12-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/precise/main/binary-amd64/Packages"]
]

local_folder_name = ppa_list[0][0]
page_to_get = "/".join([ppa_list[0][1],ppa_list[0][2]])

if not os.path.exists(local_folder_name):
  os.makedirs(local_folder_name)
else:
  print "Folder exists."

r = requests.get(page_to_get)

page_array = r.text.split("\n\n")

#packages = {};
packages = OrderedDict()
for item in page_array:
  if len(item) > 0:
    lines = item.split("\n")
    #package = {};
    package = OrderedDict()
    for line in lines:
      line_array = line.split(":")
      package[line_array[0]] = line_array[1][1:]
    #packages.append(package)
    #packages[package['Package']] = {};
    packages[package['Package']] = OrderedDict()
    packages[package['Package']].update(package)
    #print json.dumps(package, indent=2)
#print json.dumps(packages, indent=2)
with open(os.path.join(local_folder_name, 'Packages.json'), 'w') as outfile:
  json.dump(packages, outfile, indent=2)

#http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
from math import log
unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'
size = 0
for key_name, package in packages.iteritems():
  size = size + int(package['Size'])
print sizeof_fmt(size)

def requests_download_file(url_to_download, local_folder_name):
  #import requests
  #import os
  r = requests.get(url_to_download, stream=True)
  if r.status_code == 200:
    file_name = r.url.split('?')[0].split('/')[-1]
    file_path = os.path.join(local_folder_name, file_name)
    if not os.path.exists(local_folder_name):
      os.makedirs(local_folder_name)
    print "Downloading " + file_name + "..."
    with open(file_path, 'wb') as binaryfile:
      for chunk in r.iter_content(1024):
        binaryfile.write(chunk)
  else:
    print str(r.status_code) + ": " + url_to_download
for key_name, package in packages.iteritems():
  #print package['Filename']
  minor_path = os.path.sep.join(package['Filename'].split('/')[:-1])
  #print os.path.join(local_folder_name, minor_path)
  requests_download_file("/".join([ppa_list[0][1], package['Filename']]), os.path.join(local_folder_name, minor_path))
requests_download_file("/".join([ppa_list[0][1], ppa_list[0][2] + ".gz"]), local_folder_name)

import subprocess
subprocess.Popen(['mkisofs', '-o', local_folder_name + ".iso", local_folder_name])
