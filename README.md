# securityonion-utils
Miscellaneous utilities I've made for interacting with Security Onion

##Usage Examples

###get_mta.py

$ python securityonion-utils/get_mta.py -l
```
traffic, blog, or guest? traffic
2016-02-06      Network alerts at Cupid's Arrow Online.
2016-01-07      Alerts on 3 different hosts.
2015-11-24      Goofus and Gallant.
2015-11-06      Email Roulette.
2015-10-28      Midge Figgins infected her computer.
2015-10-13      Halloween-themed host names.
2015-09-23      Finding the root cause.
2015-09-11      A Bridge Too Far Enterprises.
2015-08-31      What's the EK? - What's the payload?
2015-08-07      Someone was fooled by a malicious email.
2015-07-24      Where'd the CryptoWall come from?
2015-07-11      An incident at Pyndrine Industries.
2015-06-30      Identifying the EK and infection chain.
2015-05-29      No answers, only hints for the incident report.
2015-05-08      You have the pcap.  Now tell us what's going on.
2015-03-31      Identify the activity.
2015-03-24      Answer questions about this EK activity.
2015-03-09      Answer questions about this EK activity.
2015-03-03      See alerts for Angler EK.  Now do a summary.
2015-02-24      Helping out an inexperienced analyst.
2015-02-15      Documenting a Nuclear EK infection.
2015-02-08      Mike's computer is "acting weird."
2015-01-18      Answering questions about EK traffic.
2015-01-09      Windows host visits a website, gets EK traffic.
2014-12-15      1 pcap, 3 Windows hosts, and 1 EK.
2014-12-08      Questions about EK traffic.
2014-12-04      Questions about EK traffic.
2014-11-23      Questions about EK traffic.
2014-11-16      Questions about EK traffic.
```
$ python securityonion-utils/get_mta.py -c traffic -d 2016-02-06
```
Downloading 2016-02-06-traffic-analysis-exercise.pcap...
```

###mirror_repo.py

$ python securityonion-utils/mirror_repo.py --iso

```
AVAILABLE REPOSITORIES:
0       so-14-stable-x64
1       so-14-test-x64
2       so-12-stable-x64
3       so-12-test-x64
4       ubu-14-main-x64
Repo number: 0
Retrieving Repo so-14-stable-x64...
Folder "so-14-stable-x64" already exists.
Downloading Packages.gz...
Downloading InRelease...
Downloading Release...
Downloading Release.gpg...
Expected Repo size: 348.3 MB
Downloading tcpflow_1.4.4+repack1-2securityonion1_amd64.deb...
Downloading sphinxsearch_2.1.9-release-0ubuntu16~trusty_amd64.deb...
Downloading tcl-tls_1.6+dfsg-3ubuntu1securityonion1_amd64.deb...
Downloading tcl8.6-doc_8.6.1-4ubuntu1securityonion3_all.deb...
Downloading tcl8.6_8.6.1-4ubuntu1securityonion3_amd64.deb...
<SNIP>
Downloading securityonion-samples-shellshock_20140926-0ubuntu0securityonion1_all.deb...
Downloading securityonion-samples-mta_20150103-0ubuntu0securityonion1_all.deb...
Downloading securityonion-elsa-perl_20151011-1ubuntu1securityonion8_all.deb...
Downloading securityonion-iso_20151016-1ubuntu1securityonion2_all.deb...
Downloading securityonion-ndpi_1.7.1-1ubuntu1securityonion3_amd64.deb...
skitheslicer:~/workspace (master) $ I: -input-charset not specified, using utf-8 (detected in locale settings)
  2.80% done, estimate finish Wed Feb 10 19:48:50 2016
  5.60% done, estimate finish Wed Feb 10 19:48:50 2016
  8.40% done, estimate finish Wed Feb 10 19:48:50 2016
 11.19% done, estimate finish Wed Feb 10 19:48:50 2016
 13.99% done, estimate finish Wed Feb 10 19:48:50 2016
<SNIP>
 86.69% done, estimate finish Wed Feb 10 19:48:52 2016
 89.49% done, estimate finish Wed Feb 10 19:48:52 2016
 92.28% done, estimate finish Wed Feb 10 19:48:53 2016
 95.08% done, estimate finish Wed Feb 10 19:48:53 2016
 97.88% done, estimate finish Wed Feb 10 19:48:53 2016
Total translation table size: 0
Total rockridge attributes bytes: 30719
Total directory bytes: 180224
Path table size(bytes): 2316
Max brk space used 55000
178799 extents written (349 MB)
```
$ python securityonion-utils/mirror_repo.py -u old-Packages.gz
```
AVAILABLE REPOSITORIES:
0       so-14-stable-x64
1       so-14-test-x64
2       so-12-stable-x64
3       so-12-test-x64
4       ubu-14-main-x64
Repo number: 1
Retrieving Repo so-14-test-x64...
Folder "so-14-test-x64" already exists.
Downloading Packages.gz...
Downloading securityonion-networkminer_20160210-1ubuntu1securityonion1_all.deb...
Downloading securityonion-nsmnow-admin-scripts_20120724-0ubuntu0securityonion129_all.deb...
Downloading securityonion-pfring-module_20121107-0ubuntu0securityonion25_all.deb...
Downloading securityonion-pfring-userland_20160204-1ubuntu1securityonion2_amd64.deb...
Downloading securityonion-pfring-devel_20121107-0ubuntu0securityonion9_all.deb...
Downloading securityonion-pfring-ld_20120827-0ubuntu0securityonion9_all.deb...
Downloading securityonion-pfring-daq_20121107-0ubuntu0securityonion12_amd64.deb...
```
