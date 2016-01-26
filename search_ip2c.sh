#!/bin/bash/
# By https://github.com/SkiTheSlicer
# Usage: bash search_ip2c.sh <ip.address.to.find>
# Reference: ip2c.tcl

IFS='.' read -a arrayIP <<< "$1"

o1=${arrayIP[0]}
o2=${arrayIP[1]}
o3=${arrayIP[2]}
o4=${arrayIP[3]}

n1=$(expr $o1 \* 16777216)
n2=$(expr $o2 \* 65536)
n3=$(expr $o3 \* 256)

ip=$(expr $n1 + $n2 + $n3 + $o4)

mysql -u root -D securityonion_db -e 'SELECT * FROM ip2c WHERE 'start_ip'<='$ip' AND 'end_ip'>='$ip''
