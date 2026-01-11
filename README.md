# Inet quota

A basic quota script and server for linux using iptables.

## Get started

Clone this repository in a home directory.

Ensure `iptables` is up and running.

Periodically call script `sudo crontab -e` where `johndoe` is your user:

`* * * * * /usr/bin/python3 /home/johndoe/inet-quota/inet-quota.py /home/johndoe/inet-quota/conf.json /home/johndoe/inet-quota/data`

## Raspberry Pi OS Lite as gateway

Install prerequisites:

```bash
sudo apt update -y
sudo apt install iptables -y
```

Set static IP for your gateway where `192.168.2.1` is the ip address of the wlan interface:

```bash
sudo nmcli con mod QUOTA_WLAN_SSID +ipv4.addresses 192.168.2.1/24
sudo nmcli con up QUOTA_WLAN_SSID
```

Activate packet transfer:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

Set NAT where `eth0` simulates the wan:

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

Change default gateway in the DHCP settings.