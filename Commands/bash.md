Personal Commands memo/scripts for Debian home server management-ish  
<sup> (since my memory is terrible) </sup>

License does not apply here .

# Storage

## Drive & SAS Controller temp check

Dumb script to print device name & temp of one megaraid controller (`/c0`) and other disks.

Need [storcli64](https://docs.broadcom.com/docs/STORCLI_SAS3.5_P35.zip)
for SAS drive controllers, but you can comment out that line if you don't use one.


```shell
#!/bin/bash

echo "--- SAS Controller ---"
sudo /opt/MegaRAID/storcli/storcli64 /c0 show boardname temperature | grep -E "Board Name|temp"

for d in $(lsblk -npdo KNAME); do
   printf "\n\n--- %s ---\n" "$d"
   sudo smartctl -iA "$d" | grep -E "Product|Temperature|Device Model"
done
```

```text
--- SAS Controller ---
Board Name                      LSI3008-IR
ROC temperature(Degree Celsius) 53


--- /dev/sdb ---
Device Model:     TOSHIBA HDWQ140
194 Temperature_Celsius     0x0022   100   100   000    Old_age   Always       -       43 (Min/Max 24/51)


--- /dev/sdc ---
Product:              ST8000NM001A
Temperature Warning:  Enabled
Current Drive Temperature:     48 C
Drive Trip Temperature:        60 C

...
```


## Enable SMART offline data collection

Some drives(TAMMUZ ssd especially) or SAS drives may not support it

```shell
for d in $(lsblk -npdo KNAME); do sudo smartctl $d -o on; done
```


## Validate SMART Test Schedule

```shell
sudo smartd -q showtests
```

```text
Totals [Thu Sep 25 22:25:34 2025 KST - Wed Dec 24 22:25:34 2025 KST]:
Device: /dev/disk/by-id/wwn-... [SAT], will do   1 test of type L
Device: /dev/disk/by-id/wwn-... [SAT], will do   3 tests of type S
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type C
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type O
Device: /dev/disk/by-id/wwn-... [SAT], will do   1 test of type L
Device: /dev/disk/by-id/wwn-... [SAT], will do   3 tests of type S
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type C
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type O
Device: /dev/disk/by-id/wwn-..., will do   1 test of type L
Device: /dev/disk/by-id/wwn-..., will do   3 tests of type S
Device: /dev/disk/by-id/wwn-..., will do   1 test of type L
Device: /dev/disk/by-id/wwn-..., will do   3 tests of type S
Device: /dev/disk/by-id/wwn-... [SAT], will do   1 test of type L
Device: /dev/disk/by-id/wwn-... [SAT], will do   3 tests of type S
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type C
Device: /dev/disk/by-id/wwn-... [SAT], will do   0 tests of type O
Device: /dev/disk/by-id/ata-... [SAT], will do   1 test of type L
Device: /dev/disk/by-id/ata-... [SAT], will do   3 tests of type S
Device: /dev/disk/by-id/ata-... [SAT], will do   0 tests of type C
Device: /dev/disk/by-id/ata-... [SAT], will do   0 tests of type O
```

## Fetch Disk by-id

```shell
ls -l /dev/disk/by-id/ | grep -v part | grep wwn

# or use this for few annoying drive that doesn't have wwn
ls -l /dev/disk/by-id/ | grep -v part
```

```text
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sda
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sdg
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sdc
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sdd
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sdb
lrwxrwxrwx 1 root root  9 Aug 15 05:15 wwn-... -> ../../sde
```


## Watch Raid Status

```shell
watch cat /proc/mdstat
```

```shell
for d in $(ls /dev | grep -E "md[0-9]"); do sudo mdadm --detail /dev/$d; echo ""; done
```


## Disk Activity

(honestly just htop io tab was good enough)

```shell
sudo iotop -oP
```

```shell
watch iostat -h
```


## Benchmark disk speed

`hdparm` will complain about SAS drives but still will work regardless.
Also displays temp because we're gonna run `smartctl` anyway.

```shell
for d in $(lsblk -npdo KNAME); do
        printf "\n\n--- %s ---\n" "$d"
        sudo smartctl -iA "$d" | grep -E "Product|Temperature|Device Model"
        sudo hdparm -tT --direct "$d" | grep Timing
done
```

```text
--- /dev/sda ---
Device Model:     WDC WD40EZRZ-00GXCB0
194 Temperature_Celsius     0x0022   118   103   000    Old_age   Always       -       32
 Timing O_DIRECT cached reads:   814 MB in  2.00 seconds = 407.45 MB/sec
 Timing O_DIRECT disk reads: 522 MB in  3.00 seconds = 173.82 MB/sec


--- /dev/sdb ---
Device Model:     TOSHIBA HDWQ140
194 Temperature_Celsius     0x0022   100   100   000    Old_age   Always       -       40 (Min/Max 24/52)
 Timing O_DIRECT cached reads:   812 MB in  2.00 seconds = 405.95 MB/sec
 Timing O_DIRECT disk reads: 586 MB in  3.00 seconds = 195.26 MB/sec


--- /dev/sdc ---
Product:              ST8000NM001A
Temperature Warning:  Enabled
Current Drive Temperature:     41 C
Drive Trip Temperature:        60 C
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 Timing O_DIRECT cached reads:   804 MB in  2.00 seconds = 402.38 MB/sec
 Timing O_DIRECT disk reads: 768 MB in  3.00 seconds = 255.97 MB/sec


--- /dev/sdd ---
Product:              ST8000NM001A
Temperature Warning:  Enabled
Current Drive Temperature:     40 C
Drive Trip Temperature:        60 C
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 Timing O_DIRECT cached reads:   806 MB in  2.00 seconds = 402.69 MB/sec
 Timing O_DIRECT disk reads: 768 MB in  3.00 seconds = 255.78 MB/sec


--- /dev/sde ---
Device Model:     TAMMUZ SSD
194 Temperature_Celsius     0x0022   100   100   050    Old_age   Always       -       31
 Timing O_DIRECT cached reads:   942 MB in  2.00 seconds = 471.03 MB/sec
 Timing O_DIRECT disk reads: 1508 MB in  3.00 seconds = 502.30 MB/sec


--- /dev/sdf ---
Device Model:     Samsung SSD 860 EVO 500GB
190 Airflow_Temperature_Cel 0x0032   072   053   000    Old_age   Always       -       28
 Timing O_DIRECT cached reads:   872 MB in  2.00 seconds = 435.79 MB/sec
 Timing O_DIRECT disk reads: 1496 MB in  3.00 seconds = 498.22 MB/sec


--- /dev/sdg ---
Device Model:     TOSHIBA DT01ACA200
194 Temperature_Celsius     0x0002   181   181   000    Old_age   Always       -       33 (Min/Max 22/46)
 Timing O_DIRECT cached reads:   740 MB in  2.00 seconds = 370.16 MB/sec
 Timing O_DIRECT disk reads: 592 MB in  3.01 seconds = 196.92 MB/sec
```


## Disk sleep

As someone who ran WD Blue & Toshiba N300 for 40k hours nonstop idk if this is strictly necessary...

Spindown after 30 min (`-S 241`) & APM level w/o spindown(to not interrupt `-S`) (`-B 128`):
```shell
for d in $(lsblk -npdo KNAME); do
        printf "\n\n--- %s ---\n" "$d"
        sudo hdparm -S 241 -B 128 "$d"
done
```

Unsupported devices will throw IO error:
```text
--- /dev/sda ---

/dev/sda:
 setting Advanced Power Management level to 0x80 (128)
 HDIO_DRIVE_CMD failed: Input/output error
 setting standby to 241 (30 minutes)
 APM_level      = not supported


--- /dev/sdb ---

/dev/sdb:
 setting Advanced Power Management level to 0x80 (128)
 setting standby to 241 (30 minutes)
 APM_level      = 128


--- /dev/sdc ---

/dev/sdc:
 setting Advanced Power Management level to 0x80 (128)
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 HDIO_DRIVE_CMD failed: Input/output error
 setting standby to 241 (30 minutes)
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 HDIO_DRIVE_CMD(setidle) failed: Input/output error
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00


--- /dev/sdd ---

/dev/sdd:
 setting Advanced Power Management level to 0x80 (128)
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 HDIO_DRIVE_CMD failed: Input/output error
 setting standby to 241 (30 minutes)
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00
 HDIO_DRIVE_CMD(setidle) failed: Input/output error
SG_IO: bad/missing sense data, sb[]:  72 05 20 00 00 00 00 1c 02 06 00 00 cf 00 00 00 03 02 00 01 80 0e 00 00 00 00 00 00 00 00 00 00


--- /dev/sde ---

/dev/sde:
 setting Advanced Power Management level to 0x80 (128)
 setting standby to 241 (30 minutes)
 APM_level      = 128


--- /dev/sdf ---

/dev/sdf:
 setting Advanced Power Management level to 0x80 (128)
SG_IO: bad/missing sense data, sb[]:  f0 00 05 04 51 40 80 0a 00 00 00 00 21 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
 setting standby to 241 (30 minutes)
 APM_level      = not supported


--- /dev/sdg ---

/dev/sdg:
 setting Advanced Power Management level to 0x80 (128)
 setting standby to 241 (30 minutes)
 APM_level      = 128
```

Using with `sudo powertop --auto-tune` might save you some extra, with pci ASPM on supported devices too. 


## Mount info display

```shell
findmnt -T PATH
```

When checking the current dir's mount info:

```text
...$ findmnt -T .
/      /dev/sdb2 ext4   rw,noatime,errors=remount-ro
```

<br>

---

# Network

## Network Activity

```shell
sudo tcptrack -i INTERFACE_NAME
```


## Routing Table List

All ip commands can be abbreviated to first letter only.
(e.g. `ip route show table 0` == `ip r s t 0`)

```shell
# show main table
ip route
```

```shell
# show all table
ip route show table all
# or
ip route show table 0
```

```text
default via 192.168.0.1 dev wlo1 proto dhcp src 192.168.0.a metric 600 
10.b.c.0/24 dev CONF_NAME proto kernel scope link src 10.b.c.d metric 50 
192.168.0.0/24 dev CONF_NAME scope link
192.168.0.0/24 dev wlo1 proto kernel scope link src 192.168.0.a metric 600 
```


## Routing Rule Add

For specific subnet to specific dev, implicit scope link:

```shell
ip route add ZE_SUBNET_GOES_HERE dev DEVICE
# ip route add 192.168.0.0/24 dev wlan0
```

Specified gateway
```shell
ip route add SUBNET via GATEWAY dev DEVICE
# ip route add 192.168.0.0/24 via 192.168.0.1 dev wlan0
```


## Routing Rule Delete

Add but Del

```shell
ip route del REST_OF_STRING_YOU_WROTE_IN_ADD
# ip route del 192.168.0.0/24 dev wlan0
```


## IP Assign

```shell
ip addr add ADDRESS dev DEVICE
# ip route add 192.168.0.123/24 dev wlan0
```


## Wireguard Connect

Assuming you already have valid conf

```shell
sudo nmcli connection import type wireguard file /path/to/conf/CONF_NAME.conf
```

Network manager(`nmcli`) will set low metric route (when `AllowedIPs = 0.0.0.0/0`)
so all traffic will flow thru wireguard unless speficied in other routing rules.

(visible in `ip route show table 0`, lower metric(cost) == higher priority)


## Wireguard check

```shell
sudo wg show
```

```text
interface: -
  public key: -
  private key: -
  listening port: -
  fwmark: -

peer: -
  preshared key: -
  endpoint: -
  allowed ips: 0.0.0.0/0
  latest handshake: 1 minute, 16 seconds ago
  transfer: 523.93 MiB received, 16.72 MiB sent
```


## Wireguard Remote LAN Access

If you can't access remote's local net, it could be overlapping subnet,
which could happen frequently between same vender's routers.

e.g. for `192.168.0.0/24`:

```text
> ip r
default via 192.168.0.1 dev wlo1 proto dhcp src 192.168.0.a metric 600
10.b.c.0/24 dev CONF_NAME proto kernel scope link src 10.b.c.d metric 50
192.168.0.0/24 dev wlo1 proto kernel scope link src 192.168.0.a metric 600
```

```shell
sudo ip route add 192.168.0.0/24 dev CONF_NAME
# unspecified metric considered 0 by default
```

```text
> ip r
default via 192.168.0.1 dev wlo1 proto dhcp src 192.168.0.a metric 600 
10.b.c.0/24 dev CONF_NAME proto kernel scope link src 10.b.c.d metric 50 
192.168.0.0/24 dev CONF_NAME scope link
192.168.0.0/24 dev wlo1 proto kernel scope link src 192.168.0.a metric 600 
```

<br>

---

# Access

## SSH Log

```shell
sudo journalctl _COMM=sshd | tail -n 100
```

## SFTP Log

```shell
sudo journalctl _COMM=sftp-server | tail -n 100
```

---

# NAS

## Cert New

```shell
sudo certbot certonly --standalone -d domain0,domain1,domain2
```

## Cert Renew (nginx)

cron job script

```shell
#!/bin/bash

sudo systemctl stop nginx
sudo /usr/bin/certbot renew
sudo systemctl start nginx
```

## Nextcloud Manual Update

Sometimes need to do this

```shell
#!/bin/bash

cd /var/www/nextcloud/updater
sudo -u www-data php updater.phar
```

---

# Virtualization

## IOMMU Check


---

# Docker

## Cleanup

```shell
docker system prune -a
```

## Update Portainer

```shell
#!/bin/bash

sudo docker stop portainer
sudo docker rm portainer
sudo docker pull portainer/portainer-ce:latest
sudo docker run -d -p 8000:8000 -p 9443:9443 --pull=always --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

---

# Email

## msmtp + gmail

Recommended to create entirely new gmail for this purpose, as one have to store app password
in plain text. I'm using this for smartctl reports.

(and FU Tammuz RXK550, this bastard already has bad sector & realloc
to reserve but not cleared pending sector count, making smartctl sending mail EVERY FREAKIN DAY.) 

```shell
sudo apt install msmtp msmtp-mta
sudo chmod 644 /etc/msmtprc
# ^^^ do this if other account also need to mail in same addr, i.e. reports in nas.
# otherwise for per-user follow this instead: https://superuser.com/a/351888/1252755  
```

in `/etc/msmtprc`:
```text
defaults
auth on
tls  on
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile /var/log/msmtp.log

# Gmail configuration
account gmail
host    smtp.gmail.com
port    587
from    bla@gmail.com
user    bla
password some_google_app_password

account default: gmail
```

test via:
```shell
echo "test mail" | mail some_other_email@gmail.com
```
