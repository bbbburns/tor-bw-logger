#!/usr/bin/python
import os
import sys
import glob
import time
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def print_graph(log_dir, data_frame, graph_type, relay_name):
  """Print the DataFrame as a PNG
  Take in the log directory, data frame, and type (INBOUND/OUTBOUND)
  """
  todays_date = time.strftime('%Y-%m-%d')
  graph_title = relay_name + " Relay Bandwidth: bits per second " + graph_type + " (1min sample)"
  graph_fname = relay_name + "_" + todays_date + "_"+ graph_type + "_bps_1min.png"
  save_path = os.path.join(log_dir, graph_fname)
  data_frame.plot(
          title=graph_title,
          legend=True,
          figsize=(50, 10),
          subplots=False)
  plt.legend(loc="best")
  plt.ylabel("bits per second")
  plt.xlabel("Time: America/New_York. Tick = 1min")
  fig = plt.gcf()
  fig.savefig(save_path)
  return


def find_latest_log(log_dir):
  """The most recent complete log will have the most recent date
  embedded in the file name. e.g. tor_bw.log.2014-12-26
  """
  search_string = os.path.join(log_dir, "tor_bw.log.*")
  search_results = glob.glob(search_string)
  if not search_results:
    print "No matching log files found!"
    sys.exit(1)
  else:
    latest_log = max(search_results, key=os.path.getctime)
  return latest_log

def main():
  """Search log dir for files. Parse most recent file.
  Log File Names: tor_bw.log-[date]
  Log File Format: Epoch time, Bytes In, Bytes Out
  Build graphs. Separate IN and OUT
    x = minute
    y = Max bps Out, Max bps In, Avg bps Out, Avg bps In, Min bps Out, Min bps In
  """
  parser = argparse.ArgumentParser(description=
             "Parse the log_dir location for tor bw logs and generate graphs.")
  parser.add_argument("relay_name", help="Name of the Tor relay.")
  parser.add_argument("log_dir", help="Location of tor-log-bw.py output logs.")
  args = parser.parse_args()

  log_dir = args.log_dir
  relay_name = args.relay_name
  
  latest_log = find_latest_log(log_dir)
  #print "The latest log is %s" % latest_log
  
  #Now that we have the latest_log, read it in and process it
  header_row = ["TimeStamp", "BytesIn", "BytesOut"]
  #print "about to read in CSV"
  df = pd.read_csv(latest_log, index_col=0, names=header_row, header=None, comment="S")
  df.index = pd.to_datetime((df.index.values*1e9).astype(int)).tz_localize("UTC")
  df.index = df.index.tz_convert("America/New_York")

  #DataFrame exists now as df with Bytes per second
  #df.plot(title="Relay Bandwidth: Bytes Per Second", legend=True, figsize=(50, 10),subplots=False)
  #plt.legend(loc="best")
  #fig = plt.gcf()
  #fig.savefig("bytes_per_second.png")
  
  #Create a custom how method for resampling tor bw data
  tor_dict = {'Avg bps':np.mean, 'Min bps':np.min, 'Max bps':np.max}

  #This WILL NOT WORK. Cannot pass a custom how dict on a DF :( Split to TS
  #print df.resample("1Min", how='tor_dict')

  #print "Resampling In Bytes"
  df_in = df['BytesIn'].resample("1Min", how=tor_dict)
  df_in_bits = df_in * 8
  print_graph(log_dir, df_in_bits, "INBOUND", relay_name)
  
  #print "Resampling Out Bytes"
  df_out = df['BytesOut'].resample("1Min", how=tor_dict)
  df_out_bits = df_out * 8
  print_graph(log_dir, df_out_bits, "OUTBOUND", relay_name)


if __name__ == '__main__':
  main()
