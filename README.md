SLM Distraction Tracker
===

Web interface for visualizing browsing history on a timeline.

## Architecture

The system consists of the following components:

1. **PPPTP VPN server** with associated scripts that log connect/disconnect events and launch packet loggers on connection
2. **PostgreSQL database** that holds logged connection and browsing events from the VPN server, as well as metadata
   for the web interface
3. **Flask web interface** that authenticates users against the db and allows them to view their browsing history.


## Setup PPTP VPN Server
Install on centos machine: `sudo yum install pptpd.x86_64 -y`

Configure the PPTP settings. The "ppp" configuration files are important for pptpd. First, configure `/etc/ppp/options.pptpd`, as follows. If desired, you may change the DNS servers:
```
name pptpd
refuse-pap
refuse-chap
refuse-mschap
require-mschap-v2
require-mppe-128
proxyarp
lock
nobsdcomp
novj
novjccomp
nologfd
ms-dns 8.8.8.8
ms-dns 8.8.4.4
```

Configure ppp config file at `/etc/ppp/options.pptpd`

Next, add users to the PPTP VPN service by editing `/etc/ppp/chap-secrets`. Change the username and passwords accordingly.
```
vultr1  pptpd   P@$$w0rd  *
vultr2  pptpd   P@$$w0rd2  *
```

Configure the pptpd daemon settings by editing `/etc/pptpd.conf`. Use the following example configuration. You can change the IP address ranges if needed:
```
option /etc/ppp/options.pptpd
logwtmp
localip 192.168.80.1
remoteip 192.168.80.101-200 # change the range if needed
```

Edit `/etc/sysctl.conf` to enable IP forwarding:
```
sed -i 's/^net.ipv4.ip_forward.*/net.ipv4.ip_forward = 1/g' /etc/sysctl.conf
sysctl -p
```

Configure routing with iptables:
```
iptables -A INPUT -m state --state NEW -m tcp -p tcp --dport 1723 -j ACCEPT
iptables -t nat -A POSTROUTING -o eth0 -s 192.168.80.0/24 -j MASQUERADE
service iptables save
service iptables start
```

Start the service: `service pptpd start`

Your PPTP server setup is complete. Now you can connect to your own PPTP VPN server from your PC or mobile device.

[Source for installation instructions ](https://www.vultr.com/docs/setup-pptp-vpn-server-on-centos-6)


## Making Changes
This section explains where to go to make changes

##### Updating scripts

Real copies of scripts in `core_scripts` dir are in `/etc/ppp/`. Changes made in `core_scripts` should eventually be copied there.


## Mobile Device Connection
Use the speciic setttings for each platform to connect to the VPN network.
##### Android
- Go to `Settings` >> `More` >> VPN >> Click `+` button
- Type `SLM VPN` as Name; Select `PPTP`as Type; `slm.smalldata.io` as Server address
- Make sure `PPP encryption (MPPE)` is checked and then `Save`
- Click on the newly added VPN, `SLM VPN` and enter your Username and Password to connect. You should see `Connected` if successful.

### Computer Connection

##### Mac device
- Click Wi-Fi icon  >> Open Network Preferences
- Click `+` sign at bottom left corner
- Select `VPN` as Interface, `PPTP` as VPN Type, and type `SLM VPN` as Service Name
- Click `Create`
- Make sure Configuration is set as `Default`
- Type `slm.smalldata.io` as Server Address and enter `your VPN username` as Account Name
- Click Authentication Settings and enter `your VPN password` >> Click OK
- Select the checkbox for `Show VPN status` in menu bar so you know when you are connected/disconnected
- Click `Advanced` >> uncheck box `Disconnect when user logs out` (make sure other boxes are checked) >> Click OK
- Click `Connect` (button under Encryption) >> `Apply` >> `Save Configuration` (ignore warnings for now)
- Click `Advanced` then `DNS` and `+` on bottom left. Add two entries: `8.8.8.8`  and `8.8.4.4`. Click `Ok`.
- Make sure you see that the Connect Time is counting otherwise you are still not connected and have to click `Connect` again.
- All done. Your VPN network is now active.


## Mac auto-connect VPN
