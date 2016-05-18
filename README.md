SLM Distraction Tracker
===

Web interface for visualizing browsing history on a timeline.

## Architecture

The system consists of the following components:

1. **PPPTP VPN server** with associated scripts that log connect/disconnect events and launch packet loggers on connection
2. **PostgreSQL database** that holds logged connection and browsing events from the VPN server, as well as metadata
   for the web interface
3. **Flask web interface** that authenticates users against the db and allows them to view their browsing history.

## Installation

TBC
