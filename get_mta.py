#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
import argparse
import os

def retrieve_page(page_to_get):
  r = requests.get(page_to_get)
  soup = BeautifulSoup(r.text, "html5lib")
  return soup

def list_pcaps(cat):
  base_url = "http://malware-traffic-analysis.net"
  if cat == "traffic":
    landing_url = "/".join([base_url, "training-exercises.html"])
  elif cat == "blog":
    soup = retrieve_page(base_url)
    years = soup.find_all("a", class_="list_header")
    choice = ""
    while len(choice) != 4:
      for year in years:
        if len(year.text) == 4:
          print year.text
      choice = raw_input('Specify Year: ')
    landing_url = "/".join([base_url, choice, "index.html"])
  elif cat == "guest":
    landing_url = "/".join([base_url, "guest-blog-entries.html"])
  soup = retrieve_page(landing_url)
  #a = soup.find_all("a", class_="main_menu", class_="list_header", href=re.compile("/index.html"))
  li = soup.find_all("li")
  for item in li:
    pcap_date = item.find("a", class_="list_header")
    pcap_desc = item.find("a", class_="main_menu")
    if pcap_date and pcap_desc:
      print pcap_date.text + "\t" + pcap_desc.text.replace("Traffic analysis exercise - ","")

def find_pcap(cat, date_of_pcap):
  base_url = "http://malware-traffic-analysis.net"
  if cat == "traffic":
    landing_url = "/".join([base_url, "training-exercises.html"])
    #hrefs are in yyyy/mm/dd/index.html format
  elif cat == "blog":
    landing_url = "/".join([base_url, date_of_pcap[:4], "index.html"])
    #hrefs are in mm/dd/index.html format
  elif cat == "guest":
    landing_url = "/".join([base_url, "guest-blog-entries.html"])
    #hrefs are in yyyy/mm/dd/index.html format
  soup = retrieve_page(landing_url)
  found = soup.find("a", text=date_of_pcap)
  if found["href"][:4] == date_of_pcap[:4]:
    soup2 = retrieve_page("http://malware-traffic-analysis.net/" + found["href"])
    found2 = soup2.find("a", href=re.compile(".pcap"))
    pcap = "/".join(["http://malware-traffic-analysis.net", found["href"].replace("/index.html", ""), found2["href"]])
  else:
    soup2 = retrieve_page("http://malware-traffic-analysis.net/" + date_of_pcap[:4] + "/" + found["href"])
    found2 = soup2.find("a", href=re.compile(".pcap"))
    pcap = "/".join(["http://malware-traffic-analysis.net", date_of_pcap[:4], found["href"].replace("/index.html", ""), found2["href"]])
  return pcap

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

def parse_arguments():
  #import argparse
  #import os
  parser = argparse.ArgumentParser(
    prog='get-mta.py',
    description='List and Download PCAPs from malware-traffic-analysis.net',
    epilog='Created by SkiTheSlicer (https://github.com/SkiTheSlicer)')
  parser.add_argument('-c', '--category',
                      nargs='?',
                      help='\'traffic\' for exercises, \'blog\' for blog posts, or \'guest\' for guest blogs')
  parser.add_argument('-l', '--list-pcaps',
                      action='store_true',
                      help='List PCAP files available.')
  parser.add_argument('-d', '--download-date',
                      nargs='?',
                      help='Download the PCAP for the date specified.')
  parser.add_argument('-o', '--output-dir',
                      nargs='?', default=".",
                      help='If supplied, download files to specific directory.')
  return parser.parse_args()

def main():
  args = parse_arguments()
  while args.category != "traffic" and args.category != "blog" and args.category != "guest":
    args.category = raw_input('traffic, blog, or guest? ')
  if args.list_pcaps:
    #traffic, blog, guest
    list_pcaps(args.category)
  elif args.download_date:
    requests_download_file(find_pcap(args.category, args.download_date), args.output_dir)
  else:
    print "Invalid switch options"

if __name__ == "__main__":
  main()
