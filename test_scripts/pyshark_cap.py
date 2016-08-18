#!/bin/env python

import sys
import pyshark

if __name__ == "__main__":
    # get the arguments from the caller regarding which interface, user, etc. we should be capturing for

    filtered_cap2 = pyshark.LiveCapture('ppp1', bpf_filter='tcp port 80 or tcp port 443', display_filter='ssl.handshake.extensions_server_name')

    for pkt in filtered_cap2.sniff_continuously():
        print "got packet? %s" % 'ssl!' if hasattr(pkt, 'ssl') else "no info"
        if hasattr(pkt, 'ssl'):
            print "SNI: %s" % pkt.ssl.handshake_extensions_server_name if hasattr(pkt.ssl, 'handshake_extensions_server_name') else "no info"

    print "done!"
