#!/usr/bin/python
import os
import requests
import json
from collections import OrderedDict
from math import log
import subprocess

def requests_webpage(page_to_get):
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
  import gzip
  with gzip.open(full_local_path, 'rb') as f:
    return f.read()

def parse_pkg_list(local_pkglist_path, local_dir_name):
  #from collections import OrderedDict
  #import os
  #import json
  #page_array = requests_webpage(repo_pkglist_url).text.split("\n\n")
  local_repo_file = os.path.join(local_dir_name, local_pkglist_path)
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
  with open(os.path.join(local_dir_name, 'Packages.json'), 'w') as outfile:
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
  repo_list = [
    ["so-14-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/trusty/main/binary-amd64/Packages.gz"],
    ["so-14-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/trusty/main/binary-amd64/Packages.gz"],
    ["so-12-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/precise/main/binary-amd64/Packages.gz"],
    ["so-12-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/precise/main/binary-amd64/Packages.gz"],
    ["ubu-14-main-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty/main/binary-amd64/Packages.gz"]
  ]

  print 'AVAILABLE REPOSITORIES:'
  for idx, entry in enumerate(repo_list):
    print str(idx) + '\t' + entry[0]
  repo_choice = int(raw_input('Repo number: '))
  local_dir_name = repo_list[repo_choice][0]
  local_dists_path = os.path.sep.join(repo_list[repo_choice][2].split('/')[:-1])
  repo_base_url = repo_list[repo_choice][1]
  repo_pkglist_url =  "/".join([repo_list[repo_choice][1],repo_list[repo_choice][2]])
  local_pkglist_path = os.path.sep.join(repo_list[repo_choice][2].split('/'))

  print 'Retrieving Repo ' + local_dir_name + '...'

  if not os.path.exists(local_dir_name):
    os.makedirs(local_dir_name)
  else:
    print "Folder \"" + local_dir_name + "\" already exists."

  requests_download_file(repo_pkglist_url, os.path.join(local_dir_name, local_dists_path))
  packages = parse_pkg_list(local_pkglist_path, local_dir_name)
  
  size = 0
  for key_name, package in packages.iteritems():
    size = size + int(package['Size'])
  print "Expected Repo size: " + sizeof_fmt(size)
  
  for key_name, package in packages.iteritems():
    minor_path = os.path.sep.join(package['Filename'].split('/')[:-1])
    requests_download_file("/".join([repo_base_url, package['Filename']]), os.path.join(local_dir_name, minor_path))
  
  subprocess.Popen(['mkisofs', '-o', local_dir_name + ".iso", local_dir_name])
  
main()
