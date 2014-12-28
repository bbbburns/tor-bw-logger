Tor BW Logger
=============

tor-bw-log.py
-------------
Log tor bandwidth using Stem once per second. Run this on a tor relay node.

tor-parse-log.py
----------------
Run via cron to parse log files once per day from relays.
tor-parse-log.py relay_name log_dir

Invoke tor-parse-log.py once per relay (keeping relay logs in separate dirs)

Output graphs currently go to log_dir.

Requires pandas, matplotlib, numpy, so run this somewhere else besides the relay.
