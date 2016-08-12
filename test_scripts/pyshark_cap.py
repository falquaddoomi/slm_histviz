#!/home/ec2-user/projects/slm_histviz/.venv/bin/python

import pyshark

filtered_cap2 = pyshark.LiveCapture('ppp0', bpf_filter='tcp port 80 or tcp port 443', display_filter='ssl.handshake.extensions_server_name')

for pkt in filtered_cap2.sniff_continuously():
    print "got packet!"
