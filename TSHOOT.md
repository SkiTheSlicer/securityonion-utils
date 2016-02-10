#Troubleshooting Security Onion tools

##Snort Rules
  - Reference '/etc/cron.d/rule-update'
```
sudo grep rule-update /var/log/cron.log | tail -n 5
```

###Snort Rule Updating (Enabled Rulesets, Last Update Attempt, # Enabled Rules, # Rules by Cat, # Enabled Rules by Cat)
Enumerate:
```
grep ^rule_url /etc/nsm/pulledpork/pulledpork.conf
grep UTC /var/log/nsm/pulledpork.log
grep -v ^# /etc/nsm/rules/downloaded.rules | wc -l
cut -d\" -f2 /etc/nsm/rules/downloaded.rules | awk '{print $1,$2}' | sort | uniq -c | sort -nr | less
grep -v ^# /etc/nsm/rules/downloaded.rules | cut -d\" -f2 | awk '{print $1,$2}' | sort | uniq -c | sort -nr | less
```

##SQueRT ip2c
  - Reference '/etc/cron.d/squert-ip2c'
```
sudo grep squert /var/log/cron.log | tail -n 5
```

###Snort Alert IP2C Updating (# Total, # Unique, Custom Search - Change IP Value)
Enumerate:
```
mysql -u root -D securityonion_db -e 'SELECT COUNT(*) FROM ip2c'
mysql -u root -D securityonion_db -e 'SELECT COUNT(DISTINCT start_ip,end_ip) FROM ip2c'
ip='192.168.10.128' && mysql -u root -D securityonion_db -e "SELECT *,INET_NTOA(start_ip),INET_NTOA(end_ip) FROM ip2c WHERE start_ip <= INET_ATON(\"$ip\") AND end_ip >= INET_ATON(\"$ip\") \G"
```
Attempt to Fix:
```
cd /var/www/so/squert/.scripts/ && sudo ./ip2c.tcl
```

###Snort Alert IP2C Mapping (# Unique, Last 25, Custom Search - Change IP Value)
Enumerate:
```
mysql -u root -D securityonion_db -e 'SELECT COUNT(DISTINCT ip) FROM mappings'
mysql -u root -D securityonion_db -e 'SELECT INET_NTOA(ip),age FROM mappings ORDER BY age DESC LIMIT 25'
ip='192.168.10.128' && mysql -u root -D securityonion_db -e "SELECT INET_NTOA(ip),age FROM mappings WHERE ip = INET_ATON(\"$ip\")"
```
Attempt to Fix:
```
sudo /usr/bin/php -e /var/www/so/squert/.inc/ip2c.php 1
sudo /usr/bin/php -e /var/www/so/squert/.inc/ip2c.php 0
```
