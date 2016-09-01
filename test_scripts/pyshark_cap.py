#!/usr/bin/python

import sys
import pyshark

from cachetools import LRUCache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data import ConnectLog, AccessLog

def print_layer(layer):
    print "\n".join([
        "%s => %s" % (k, getattr(layer, k))
        for k in layer.field_names
    ])

if __name__ == "__main__":
    try:
        (interface, username, local_ip, remote_ip) = sys.argv[1:5]
    except ValueError:
        print "USAGE: %s <interface> <username> <local_ip> <remote_ip>" % sys.argv[0]
        exit(1)

    # connect to pgdb
    engine = create_engine('postgresql://histviz_site@pgdb/slm_distraction')
    Session = sessionmaker(bind=engine)
    session = Session() # and make an actual session with which to do stuff

    connect_event = ConnectLog(
        username=username,
        status='connected',
        interface=interface,
        local_ip=local_ip,
        remote_ip=remote_ip
    )
    session.add(connect_event)
    session.commit()

    # cache of session IDs, so we can perform SNI resolution on following traffic
    tls_session_IDs = LRUCache(maxsize=4000)
    # cache of tcp stream IDs that have associated SNIs from a prior request
    stream_cache = LRUCache(maxsize=4000)
    # cache of ip -> SNI relations we've previously seen
    # very large since it's our most reliable method
    host_sni_cache = LRUCache(maxsize=32000)

    filtered_cap2 = pyshark.LiveCapture(
        interface,
        bpf_filter='tcp port 80 or tcp port 443',
        display_filter='ssl.handshake.extensions_server_name or tcp or tcp.stream'
        # override_prefs={'nameres.network_name': 'TRUE'}
    )
    filtered_cap2.set_debug()

    try:
        for pkt in filtered_cap2.sniff_continuously():
            session_id = None
            detected_sni = None
            stream_id = pkt.tcp.stream
            # be sure that we're not recording our own ip, regardless of the direction of flow
            remote_host = pkt.ip.dst_host if pkt.ip.dst_host != remote_ip else pkt.ip.src_host

            # we cache the session ID => SNI mapping for later
            if hasattr(pkt, 'ssl'):
                if hasattr(pkt.ssl, 'handshake_session_id'):
                    session_id = pkt.ssl.handshake_session_id
                if hasattr(pkt.ssl, 'handshake_extensions_server_name'):
                    detected_sni = pkt.ssl.handshake_extensions_server_name

                if detected_sni and len(detected_sni) > 0:
                    if session_id and len(session_id) > 0:
                        tls_session_IDs[session_id] = detected_sni
                    if stream_id:
                        stream_cache[stream_id] = detected_sni
                    # always put it in the host sni cache, i guess
                    host_sni_cache[remote_host] = detected_sni

            # --- debug output below ---
            # pkt.pretty_print()

            # print "**** PKT BEGIN ****"
            # for layer in pkt.layers:
            #     print "=== pkt.%s ===" % layer.layer_name
            #     print_layer(layer)
            # print "****\n"

            # actually log packet metadata now
            access_event = AccessLog(
                    username=username,
                    hostname=remote_host,
                    protocol=("https" if pkt.tcp.dstport == "443" else "http"),
                    length=pkt.length,
                    sni='<unknown>'
            )

            # include sni if it's directly available in the handshake
            # attempt to use one of our many caches if it's not (i.e. this is subsequent traffic)
            if detected_sni and len(detected_sni) > 0:
                access_event.sni = detected_sni
            elif session_id and len(session_id) > 0 and session_id in tls_session_IDs:
                access_event.sni = tls_session_IDs[session_id]
            elif stream_id and stream_id in stream_cache:
                access_event.sni = stream_cache[stream_id]
            elif remote_host in host_sni_cache:
                access_event.sni = host_sni_cache[remote_host]
            # ...else we just don't know the SNI and have to leave it unknown :(

            session.add(access_event)
            session.commit()

    except KeyboardInterrupt:
        print "*** interrupt received, attempting to exit cleanly..."

    # this will commit both the initial 'connect' event and all the accesses
    session.commit()

    # assumedly if we reach this point the interface has been closed
    # FIXME: verify the above assumption

    disconnect_event = ConnectLog(
        username=username,
        status='disconnected',
        interface=interface,
        local_ip=local_ip,
        remote_ip=remote_ip
    )
    session.add(disconnect_event)
    session.commit()

    print "...done!"
