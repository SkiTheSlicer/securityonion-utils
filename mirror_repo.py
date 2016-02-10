#!/usr/bin/python
import os
import requests
import gzip
import json
from collections import OrderedDict
from math import log
import subprocess

def requests_webpage(page_to_get):
  #import requests
  r = requests.get(page_to_get)
  return r

def requests_download_file(url_to_download, local_dir_name):
  #import requests
  #import os
  r = requests.get(url_to_download, stream=True)
  if r.status_code == 200:
    file_name = r.url.split('?')[0].split('/')[-1]
    file_path = os.path.join(local_dir_name, file_name)
    if not os.path.exists(local_dir_name):
      os.makedirs(local_dir_name)
    print "Downloading " + file_name + "..."
    with open(file_path, 'wb') as binaryfile:
      for chunk in r.iter_content(1024):
        binaryfile.write(chunk)
  else:
    print str(r.status_code) + ": " + url_to_download

def gzip_decompress_file(full_local_path):
  #import gzip
  with gzip.open(full_local_path, 'rb') as f:
    return f.read()

def parse_pkg_list(path_repo_pkglist, dir_local_base):
  #from collections import OrderedDict
  #import os
  #import json
  #page_array = requests_webpage(url_repo_pkglist).text.split("\n\n")
  local_repo_file = os.path.join(dir_local_base, path_repo_pkglist)
  page_array = gzip_decompress_file(local_repo_file).split("\n\n")
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
  with open(os.path.join(dir_local_base, 'Packages.json'), 'w') as outfile:
    json.dump(packages, outfile, indent=2)
  return packages

def sizeof_fmt(num):
  #from math import log
  #http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
  unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
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

def main():
  #[short name, url base, url dist, url arch]
  repo_list = [
    ["so-14-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/trusty", "main/binary-amd64", "Packages.gz"],
    ["so-14-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/trusty", "main/binary-amd64", "Packages.gz"],
    ["so-12-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/precise", "main/binary-amd64", "Packages.gz"],
    ["so-12-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/precise", "main/binary-amd64", "Packages.gz"],
    ["ubu-14-main-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty", "main/binary-amd64", "Packages.gz"]
  ]

  print 'AVAILABLE REPOSITORIES:'
  for idx, entry in enumerate(repo_list):
    print str(idx) + '\t' + entry[0]
  repo_choice = int(raw_input('Repo number: '))
  dir_local_base = repo_list[repo_choice][0]
  dir_repo_dist = os.path.sep.join(repo_list[repo_choice][2].split('/'))
  dir_repo_arch = os.path.sep.join(repo_list[repo_choice][2].split('/') + repo_list[repo_choice][3].split('/'))
  path_repo_pkglist = os.path.sep.join(repo_list[repo_choice][2].split('/') + repo_list[repo_choice][3].split('/') + ["Packages.gz"])
  url_repo_base = repo_list[repo_choice][1]
  url_repo_dist = "/".join([repo_list[repo_choice][1],repo_list[repo_choice][2]])
  url_repo_pkglist =  "/".join([repo_list[repo_choice][1],repo_list[repo_choice][2],repo_list[repo_choice][3], "Packages.gz"])

  print 'Retrieving Repo ' + dir_local_base + '...'

  if not os.path.exists(dir_local_base):
    os.makedirs(dir_local_base)
  else:
    print "Folder \"" + dir_local_base + "\" already exists."

  requests_download_file(url_repo_pkglist, os.path.join(dir_local_base, dir_repo_arch))
  packages = parse_pkg_list(path_repo_pkglist, dir_local_base)
  for auth_file in ['InRelease', 'Release', 'Release.gpg']:
    requests_download_file("/".join([url_repo_dist, auth_file]), os.path.join(dir_local_base, dir_repo_dist))

  size = 0
  for key_name, package in packages.iteritems():
    size = size + int(package['Size'])
  print "Expected Repo size: " + sizeof_fmt(size)

  for key_name, package in packages.iteritems():
    #url_pkg_todownload = "/".join([url_repo_base, package['Filename']])
    path_pkg_output = os.path.sep.join(package['Filename'].split('/')[:-1])
    requests_download_file("/".join([url_repo_base, package['Filename']]), os.path.join(dir_local_base, path_pkg_output))

 #Needs check for if host is Linux
  subprocess.Popen(['mkisofs', '-r', '-J', '-l', '-o', dir_local_base + ".iso", dir_local_base])

  with open(dir_local_base + ".sh", 'wb') as binaryfile:
    binaryfile.write('#!/bin/bash\n')
    binaryfile.write('sudo mount -o loop ' + dir_local_base + '.iso /mnt/\n')
    binaryfile.write('echo "deb file:/mnt/ ' + repo_list[repo_choice][2].split('/')[-1] + " " + repo_list[repo_choice][3].split('/')[0] + '" | sudo tee /etc/apt/sources.list.d/securityonion-cdrom.list\n')
    binaryfile.write('sudo apt-get update\n')
    binaryfile.write('sudo apt-get dist-upgrade\n')

main()
