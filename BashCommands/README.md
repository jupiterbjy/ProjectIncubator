Personal Commands memo/scripts for Debian home server management-ish  
<sup> (since my memory is terrible) </sup>

License does not apply here 

# Storage

## Drive & SAS Controller temp check

Dumb script to print device name & temp of one megaraid controller (`/c0`) and other disks.

Need [storcli64](https://docs.broadcom.com/docs/STORCLI_SAS3.5_P35.zip)

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

```shell
#!/bin/bash

echo "--- SAS Controller ---"
sudo /opt/MegaRAID/storcli/storcli64 /c0 show boardname temperature | grep -E "Board Name|temp"

for d in $(lsblk -npdo KNAME); do
   printf "\n\n--- %s ---\n" "$d"
   sudo smartctl -iA "$d" | grep -E "Product|Temperature|Device Model"
done
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


---

# Network

## Network Activity

```shell
sudo tcptrack -i INTERFACE_NAME
```

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
