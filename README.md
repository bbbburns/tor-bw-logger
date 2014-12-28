Tor BW Logger
=============

tor-bw-log.py
-------------
Log tor bandwidth using Stem once per second. Run this on a tor relay node.

Probably a good idea to pull these log files back to a central processing
location via rsync or some other means.

tor-parse-log.py
----------------
Run via cron to parse log files once per day from relays.
tor-parse-log.py relay_name log_dir

Invoke tor-parse-log.py once per relay (keeping relay logs in separate dirs)

Output graphs currently go to log_dir.

Requires pandas, matplotlib, numpy, so run this somewhere else besides the relay.

Support Scripts Not Added
-------------------------
###fetch_files.sh
Cron
Runs on the log server to pull the tor_bw.log files once per day from relays.

###parse_logs.sh
Cron
Runs on the log server via cron, calling tor-parse.log.py for each relay.


TODO
----
1. Build a web display portion for the finished graphs
2. Streamline the log collection and parsing. Think of how to scale this.
