SLM Distraction Tracker
===

Web interface for visualizing browsing history on a timeline.

## Architecture

The system consists of the following components:

1. a *PPPTP VPN server* with associated scripts that log connect/disconnect events and launch packet loggers on connection
2. a *postgresql database* that holds logged connection and browsing events from the VPN server, as well as metadata
   for the web interface
3. a *Flask web interface* that authenticates users against the db and allows them to view their browsing history.

## Installation

TBC