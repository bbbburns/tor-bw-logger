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
  #Find the max timestamp in the dataframe and use this to name the file
  log_date =  str(data_frame.index.max().date())
  graph_title = " ".join([log_date,
                         relay_name,
                         "Relay Bandwidth: bits per second",
                         graph_type,
                         "(1min sample)"])
  graph_fname = relay_name + "_" + log_date + "_"+ graph_type + "_bps_1min.png"
  save_path = os.path.join(log_dir, graph_fname)
  data_frame.plot(
          title=graph_title,
          legend=True,
          figsize=(50, 10),
          subplots=False)
  plt.legend(loc="best")
  plt.ylabel("bits per second")
  plt.xlabel("Time: UTC. Tick = 1min")
  fig = plt.gcf()
  fig.savefig(save_path)
  return

def find_latest_log(log_dir):
  """The most recent complete log will have the most recent date
  embedded in the file name. e.g. tor_bw.log.2014-12-26
  """
  search_string = os.path.join(log_dir, "tor_bw.log.*")
  search_results = glob.glob(search_string)
  try:
    latest_log = max(search_results, key=os.path.getctime)
  except:
    print "No Log Files Found:", sys.exc_info()[0]
    raise
  return latest_log

def main():
  """Search log dir for files. Parse most recent file.
  Log File Names: tor_bw.log-[date]
  Log File Format: Epoch time, Bytes In, Bytes Out
  Build graphs. Separate IN and OUT
    Graph In:
      x = minute
      y = min in bps, avg in bps, max in bps
    Graph Out:
      x = minute
      y = min out bps, avg out bps, max out bps
  """
  parser = argparse.ArgumentParser(description=
             "Parse the log_dir location for tor bw logs and generate graphs.")
  parser.add_argument("relay_name", help="Name of the Tor relay.")
  parser.add_argument("log_dir", help="Location of tor-log-bw.py output logs.")
  args = parser.parse_args()

  log_dir = args.log_dir
  relay_name = args.relay_name

  latest_log = find_latest_log(log_dir)

  #Now that we have the latest_log, read it in and process it
  header_row = ["TimeStamp", "BytesIn", "BytesOut"]
  df_bytes_combined = pd.read_csv(
      latest_log,
      index_col=0,
      names=header_row,
      header=None,
      comment="S")
  df_bytes_combined.index = pd.to_datetime(
      (df_bytes_combined.index.values*1e9).astype(int)).tz_localize("UTC")

  #DataFrame exists now as df with Bytes per second
  #df.plot(title="Relay Bandwidth: Bytes Per Second", legend=True, figsize=(50, 10),subplots=False)
  #plt.legend(loc="best")
  #fig = plt.gcf()
  #fig.savefig("bytes_per_second.png")

  #Create a custom how method for resampling tor bw data
  avg_min_max = {'Avg bps':np.mean, 'Min bps':np.min, 'Max bps':np.max}

  #This WILL NOT WORK. Cannot pass a custom how dict on a DF :( Split to TS
  #print df_bytes_combined.resample("1Min", how=avg_min_max)

  #print "Resampling In Bytes"
  df_in_bytes = df_bytes_combined['BytesIn'].resample("1Min", how=avg_min_max)
  df_in_bits = df_in_bytes * 8
  print_graph(log_dir, df_in_bits, "INBOUND", relay_name)

  #print "Resampling Out Bytes"
  df_out_bytes = df_bytes_combined['BytesOut'].resample("1Min", how=avg_min_max)
  df_out_bits = df_out_bytes * 8
  print_graph(log_dir, df_out_bits, "OUTBOUND", relay_name)


if __name__ == '__main__':
  main()
