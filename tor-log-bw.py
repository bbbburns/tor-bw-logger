#!/usr/bin/python
import functools
import logging
import time

from logging.handlers import TimedRotatingFileHandler

from stem.control import EventType, Controller
from stem.util import str_tools

def create_timed_rotating_log(path):
  """Create a log file that rotates at midnight to store CSV BW values"""
  logger = logging.getLogger("Rotating Log")
  logger.setLevel(logging.INFO)
  
  handler = TimedRotatingFileHandler(path,
                                     when="MIDNIGHT",
                                     interval=1,
                                     backupCount=5)
  logger.addHandler(handler)

def main():
  """Create a log file and setup the event handler for BW events"""
  with Controller.from_port(port = 9051) as controller:
    controller.authenticate()
    
    """
    TODO This try except could be eliminated and just straight up call draw_bw
    Also, we can rename this to write_csv or something
    """
    log_file = "tor_bw.log"

    create_timed_rotating_log(log_file)
    logger = logging.getLogger("Rotating Log")
    logger.info("Starting BW Event Logging")

    try:
      # This makes curses initialize and call draw_bandwidth_graph() with a
      # reference to the screen, followed by additional arguments (in this
      # case just the controller).

      log_bandwidth(controller)
    except KeyboardInterrupt:
      pass  # the user hit ctrl+c

def log_bandwidth(controller):
  """Setup the event handler and then sleep indefinitely"""
  bandwidth_rates = []
  
  # Making a partial that wraps the window and bandwidth_rates with a function
  # for Tor to call when it gets a BW event. This causes the output_file
  # and 'bandwidth_rates' to be provided as arguments whenever
  # 'bw_event_handler()' is called.

  bw_event_handler = functools.partial(_handle_bandwidth_event, bandwidth_rates)

  # Registering this listener with Tor. Tor reports a BW event each second.

  controller.add_event_listener(bw_event_handler, EventType.BW)

  """
  There was a pause of the main thread RIGHT HERE, but I deleted it
  How do we get the main thread to pause execution and just run while waiting
  for further tor BW events? This below seems like a poor hack
  """

  while True:
    try:
      time.sleep(1)

    except KeyboardInterrupt:
      print "Hit Interrupt while in loop. Exiting"
      break

def _handle_bandwidth_event(bandwidth_rates, event):
  """Process incoming BW event and call the logging function on it"""
  # callback for when tor provides us with a BW event
  cur_time = int(time.time())
  bandwidth_rates = [cur_time, event.read, event.written]
  
  log_rates(bandwidth_rates)

def log_rates(bandwidth_rates):
  """Log the BW event to the rotating log file"""
  #print bandwidth_rates

  logger = logging.getLogger("Rotating Log")
  logger.info(str(bandwidth_rates[0]) + "," + str(bandwidth_rates[1]) + "," + str(bandwidth_rates[2]))

if __name__ == '__main__':
  main()
