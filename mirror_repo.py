#!/usr/bin/python
# Created by https://github.com/SkiTheSlicer
import argparse
import os
import shutil
import sys
import gzip
import json
import subprocess
from collections import OrderedDict
from datetime import datetime
from math import log

import requests

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='mirror_repo.py',
        description='Download repository for use on an out-of-band machine.',
        epilog='Created by SkiTheSlicer (https://github.com/SkiTheSlicer)')
    parser.add_argument('-u', '--old',
                        nargs='?',
                        help='Specifies old Packages.gz to compare; will only download differences.')
    parser.add_argument('-i', '--iso',
                        action='store_true',
                        help='Download and create ISO.')
    parser.add_argument('-a', '--apt-get',
                        nargs='*',
                        help='Download package and attempt to resolve 1st level of dependencies.')
    return parser.parse_args()

def query_yes_no(question, default="yes"):
    # http://code.activestate.com/recipes/577058/
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def requests_download_file(url_to_download, local_dir_name):
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
    with gzip.open(full_local_path, 'rb') as f:
        return f.read()

def parse_pkg_list(local_repo_file):
    page_array = local_repo_file.split("\n\n")
    #packages = {};
    packages = OrderedDict()
    for item in page_array:
        if len(item) > 0:
            lines = item.split("\n")
            #package = {};
            package = OrderedDict()
            for line in lines:
                line_array = line.split(":")
                try:
                    package[line_array[0]] = line_array[1][1:]
                except IndexError:
                    continue
            #packages.append(package)
            #packages[package['Package']] = {};
            try:
                packages[package['Package']] = OrderedDict()
                packages[package['Package']].update(package)
            except KeyError:
                print 'ERROR with ' + str(package)
            #print json.dumps(package, indent=2)
    return packages

def sizeof_fmt(num):
    # http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """Human friendly file size"""
    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    elif num == 0:
        return '0 bytes'
    elif num == 1:
        return '1 byte'

def define_repo_list(date_now):
    print 'Updating Repo Pkg Lists...'
    #[short name, url base, url dist, url arch]
    repo_list = [
        ["so-14-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/trusty", "main/binary-amd64"],
        ["so-14-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/trusty", "main/binary-amd64"],
        ["sift-14-stable-x64", "http://ppa.launchpad.net/sift/stable/ubuntu", "dists/trusty", "main/binary-amd64"],
        ["remnux-14-stable-x64", "http://ppa.launchpad.net/remnux/stable/ubuntu", "dists/trusty", "main/binary-amd64"],
        ["ubu-14-main-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty", "main/binary-amd64"],
        ["ubu-14-rest-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty", "restricted/binary-amd64"],
        ["ubu-14-univ-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty", "universe/binary-amd64"],
        ["ubu-14-mult-x64", "http://us.archive.ubuntu.com/ubuntu", "dists/trusty", "multiverse/binary-amd64"],
        ["ntop-14-stable-x64", "http://packages.ntop.org/apt-stable/14.04", "x64", ""],
        ["ntop-14-stable-all", "http://packages.ntop.org/apt-stable/14.04", "all", ""],
        ["mysql-14-connector-x64", "http://repo.mysql.com/apt/ubuntu", "dists/trusty", "connector-python-2.1/binary-amd64"],
        ["inetsim", "http://www.inetsim.org/debian", "binary", ""],
        ["kali-14-main-x64", "http://http.kali.org/kali", "dists/sana", "main/binary-amd64"],
        ["kali-14-contrib-x64", "http://http.kali.org/kali", "dists/sana", "contrib/binary-amd64"],
        ["kali-14-nonfree-x64", "http://http.kali.org/kali", "dists/sana", "non-free/binary-amd64"]
    ]
    """Removed
        ["so-12-stable-x64", "http://ppa.launchpad.net/securityonion/stable/ubuntu", "dists/precise", "main/binary-amd64"],
        ["so-12-test-x64", "http://ppa.launchpad.net/securityonion/test/ubuntu", "dists/precise", "main/binary-amd64"],
        ["sift-14-devel-x64", "http://ppa.launchpad.net/sift/stable/ubuntu", "dists/devel", "main/binary-amd64"],
        ["remnux-14-devel-x64", "http://ppa.launchpad.net/remnux/stable/ubuntu", "dists/devel", "main/binary-amd64"],
    """
    repos_to_skip = []
    for repo in repo_list:
        if not os.path.exists(os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.gz']))):
            print repo[0].upper() + ':'
            requests_download_file('/'.join([repo[1],repo[2],repo[3],'Packages.gz']), '.repo')
            os.rename(os.path.join('.repo', 'Packages.gz') ,os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.gz'])))
        else:
            #print 'Repo \'' + repo[0] + '\' already downloaded today. Skipping...'
            repos_to_skip.append(repo[0])
        if not os.path.exists(os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.json']))):
            json_pkg_list = parse_pkg_list(gzip_decompress_file(os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.gz']))))
            with open(os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.json'])), 'w') as outfile:
                json.dump(json_pkg_list, outfile, indent=2)
        json_pkg_list = json.load(open(os.path.join('.repo', ''.join(['Packages-', repo[0], '-', date_now, '.json'])), 'rb'))
        size = 0
        for key_name, package in json_pkg_list.iteritems():
            size = size + int(package['Size'])
        repo.append(sizeof_fmt(size))
        #print "Expected Size of " + repo[0] + ": " + repo[4]
    if len(repos_to_skip) > 0:
        print 'Repos Already Downloaded Today (Skipped):'
        for repo in repos_to_skip:
            print '\t' + repo
    return repo_list

def main():
    date_now = datetime.now().strftime('%Y%m%d')
    args = parse_arguments()
    if args.old:
        if not args.old.endswith('gz'):
            print "Update file doesn't end in 'gz'. Exitting..."
            sys.exit(1)
        elif not os.path.exists(args.old):
            print "Update file '" + args.old + "' doesn't exist. Exitting..."
            sys.exit(1)
    repo_list = define_repo_list(date_now)
    print '\nCONFIGURED REPOSITORIES:'
    for idx, entry in enumerate(repo_list):
        print str(idx) + '\t' + entry[0]
    repo_choice = int(raw_input('Specify Repo Number: '))
    dir_local_base = repo_list[repo_choice][0]
    dir_repo_dist = os.path.sep.join(repo_list[repo_choice][2].split('/'))
    dir_repo_arch = os.path.sep.join(repo_list[repo_choice][2].split('/') + repo_list[repo_choice][3].split('/'))
    path_repo_pkglist = os.path.sep.join(repo_list[repo_choice][2].split('/') + repo_list[repo_choice][3].split('/') + ["Packages.gz"])
    url_repo_base = repo_list[repo_choice][1]
    url_repo_dist = "/".join([repo_list[repo_choice][1],repo_list[repo_choice][2]])
    url_repo_pkglist =    "/".join([repo_list[repo_choice][1],repo_list[repo_choice][2],repo_list[repo_choice][3], "Packages.gz"])

    json_packages_list = json.load(open(os.path.join('.repo', ''.join(['Packages-', repo_list[repo_choice][0], '-', date_now, '.json'])), 'rb'))

    pkgs_to_download = []
    pkgs_to_skip = []
    if args.apt_get:
        # Doesn't yet recognize pkgs_to_download, pkgs_to_skip (20160212)
        print 'Apt-Get: ' + str(args.apt_get)
        apt_deps = []
        for apt_pkg in args.apt_get:
            for key_name, package in json_packages_list.iteritems():
                if apt_pkg == key_name:
                    apt_deps.append(apt_pkg)
                    for dep in package['Depends'].split(','):
                        if dep.strip().split(' ',1)[0] not in apt_deps:
                            apt_deps.append(dep.strip().split(' ',1)[0])
        print 'Depends: ' + str(apt_deps)
        apt_missing = []
        for apt_pkg in args.apt_get:
            if apt_pkg not in apt_deps:
                apt_missing.append(apt_pkg)
        apt_urls = []
        for apt_dep in apt_deps:
            try:
                apt_urls.append('/'.join([url_repo_base, json_packages_list[apt_dep]['Filename']]))
            except KeyError:
                #print apt_dep + ' not in ' + dir_local_base
                apt_missing.append(apt_dep)
        #print 'URLs: ' + str(apt_urls)
        if len(apt_missing) > 0:
            print 'Missing: ' + str(apt_missing)
            print 'CONFIGURED REPOSITORIES:'
            for idx, entry in enumerate(repo_list):
                print str(idx) + '\t' + entry[0]
            repo_dep_choice = int(raw_input('Specify Alternate Repo Number: '))
            #url_alt_repo = "/".join([repo_list[repo_dep_choice][1],repo_list[repo_dep_choice][2],repo_list[repo_dep_choice][3], "Packages.gz"])
            #r = requests.get(url_alt_repo, stream=True)
            #from StringIO import StringIO
            #str_alt_repo = gzip.GzipFile(fileobj=StringIO(r.content), mode='rb').read()
            #json_alt_repo = parse_pkg_list(str_alt_repo)
            json_alt_repo = json.load(open(os.path.join('.repo', ''.join(['Packages-', repo_list[repo_dep_choice][0], '-', date_now, '.json'])), 'rb'))
            apt_still_missing = []
            for apt_pkg in apt_missing:
                try:
                    apt_urls.append('/'.join([repo_list[repo_dep_choice][1], json_alt_repo[apt_pkg]['Filename']]))
                except KeyError:
                    apt_still_missing.append(apt_pkg)
            #print json.dumps(json_alt_repo, indent=2)
            if len(apt_still_missing) > 0:
                print 'Still Missing: ' + str(apt_still_missing)
            #print 'URLs: ' + str(apt_urls)
            for apt_url in apt_urls:
                if not os.path.exists(os.path.join('apt-get', apt_url.split('/')[-1])):
                    requests_download_file(apt_url, 'apt-get')
                else:
                    print 'Already downloaded \'' + apt_url.split('/')[-1] + '\'. Skipping...'
    if not args.old and not args.apt_get:
        #size = 0
        #for key_name, package in json_packages_list.iteritems():
        #    size = size + int(package['Size'])
        #print 'Expected Download Size: ' + repo_list[repo_choice][4]
        #if not query_yes_no('Continue Download?'):
        #    print 'Exitting...'
        #    sys.exit(1)
        for key_name, package in json_packages_list.iteritems():
            #url_pkg_todownload = "/".join([url_repo_base, package['Filename']])
            if not os.path.exists(os.path.join(dir_local_base, os.path.sep.join(package['Filename'].split('/')))):
                path_pkg_output = os.path.sep.join(package['Filename'].split('/')[:-1])
                pkgs_to_download.append(['/'.join([url_repo_base, package['Filename']]), os.path.join(dir_local_base, path_pkg_output), package['Size']])
                #requests_download_file('/'.join([url_repo_base, package['Filename']]), os.path.join(dir_local_base, path_pkg_output))
            else:
                pkgs_to_skip.append(key_name)
                #print 'Already downloaded \'' + package['Filename'].split('/')[-1] + '\'. Skipping...'
    elif not args.apt_get:
        print 'Updating Repo "' + args.old.split(os.path.sep)[-1] + '"...'
        json_old_list = parse_pkg_list(gzip_decompress_file(args.old))
        for key_name, package in json_packages_list.iteritems():
            if json_old_list[key_name]['Filename'] != package['Filename']:
                #url_pkg_todownload = "/".join([url_repo_base, package['Filename']])
                if not os.path.exists(os.path.join(dir_local_base, os.path.sep.join(package['Filename'].split('/')))):
                    path_pkg_output = os.path.sep.join(package['Filename'].split('/')[:-1])
                    pkgs_to_download.append(['/'.join([url_repo_base, package['Filename']]), os.path.join(dir_local_base, path_pkg_output), package['Size']])
                    #requests_download_file('/'.join([url_repo_base, package['Filename']]), os.path.join(dir_local_base, path_pkg_output))
                else:
                    pkgs_to_skip.append(key_name)
                    #print 'Already downloaded \'' + package['Filename'].split('/')[-1] + '\'. Skipping...'
    if len(pkgs_to_download) > 0:
        size = 0
        for url, path, file_size in pkgs_to_download:
            size = size + int(file_size)
        print 'Expected Download Size: ' + sizeof_fmt(size)
        if not query_yes_no('Continue Download?'):
            print 'Exitting...'
            sys.exit(1)
        else:
            for url, path, file_size in pkgs_to_download:
                requests_download_file(url, path)
    else:
        # Doesn't account for apt-get yet (20160212)
        print 'No Packages to Download.'
    if len(pkgs_to_skip) > 0:
        print 'Pkgs Already Downloaded (Skipped):'
        print str(pkgs_to_skip)
    if not os.path.exists(os.path.join(dir_local_base, dir_repo_arch)):
        os.makedirs(os.path.join(dir_local_base, dir_repo_arch))
    shutil.copyfile(os.path.join('.repo', ''.join(['Packages-', repo_list[repo_choice][0], '-', date_now, '.gz'])), os.path.join(dir_local_base, dir_repo_arch, 'Packages.gz'))

    if args.iso:
        print 'Expected ISO Size: ' + repo_list[repo_choice][4]
        if not query_yes_no('Continue ISO Creation?'):
            print 'Exitting...'
            sys.exit(1)
        else:
            auths_to_skip = []
            for auth_file in ['InRelease', 'Release', 'Release.gpg']:
                if not os.path.exists(os.path.join(dir_local_base, dir_repo_dist, auth_file)):
                    requests_download_file("/".join([url_repo_dist, auth_file]), os.path.join(dir_local_base, dir_repo_dist))
                else:
                    #print 'Already downloaded \'' + auth_file + '\'. Skipping...'
                    auths_to_skip.append(auth_file)
            if len(auths_to_skip) > 0:
                print 'Auth Files Already Downloaded (Skipped):'
                print str(auths_to_skip)
            if args.apt_get:
                # Needs check for if host is Linux
                try:
                    dir_local_base = 'apt-get'
                    dpkg = subprocess.Popen(['dpkg-scanpackages', dir_local_base, '/dev/null'], stdout=subprocess.PIPE)
                    subprocess.Popen(['gzip', '-9c'], stdin=dpkg.stdout, stdout=open(os.path.join(dir_local_base, 'Packages.gz'), 'wb', 0))
                except:
                    # Make a powershell option?
                    print 'ERROR: Creating Packages.gz requires dpkg-dev'
         # Needs check for if host is Linux
            subprocess.Popen(['mkisofs', '-r', '-jcharset=utf-8', '-l', '-o', dir_local_base + ".iso", dir_local_base])
            # Make a powershell option?

            with open(dir_local_base + ".sh", 'wb') as binaryfile:
                binaryfile.write('#!/bin/bash\n')
                binaryfile.write('sudo mount -o loop ' + dir_local_base + '.iso /mnt/\n')
              # Causes problems with ntop repo (2016-02-12):
                binaryfile.write('echo "deb file:/mnt/ ' + repo_list[repo_choice][2].split('/')[-1] + " " + repo_list[repo_choice][3].split('/')[0] + '" | sudo tee /etc/apt/sources.list.d/repo-on-cdrom.list\n')
                binaryfile.write('#sudo apt-get update && sudo apt-get dist-upgrade\n')
                binaryfile.write('sudo /usr/bin/soup\n')
                binaryfile.write('sudo umount /mnt/\n')
                binaryfile.write('sudo rm /etc/apt/sources.list.d/repo-on-cdrom.list\n')        

if __name__ == "__main__":
    main()
