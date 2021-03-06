#!/usr/bin/env python

from __future__ import print_function
import sys
import shlex
import time
import cmd
import argparse
import traceback

from edtslib import util
from edtslib import ship

if __name__ == '__main__':
  print("Loading environment...")
from edtslib import env

env.configure_logging(env.global_args.log_level)
log = util.get_logger("edi")

# Now env is loaded, import the apps
from edtslib import edts
from edtslib import close_to
from edtslib import coords
from edtslib import direction
from edtslib import distance
from edtslib import find
from edtslib import galmath
from edtslib import fuel_usage
from edtslib import vsc


class EDI(cmd.Cmd):

  def __init__(self):
    # super (EDI, self).__init__()
    cmd.Cmd.__init__(self)
    self.prompt = "EDI> "
    self.state = {}

  def run_application(self, ns, args):
    try:
      args = shlex.split(args)
      app = ns.Application(args, True, self.state)
      app.run()
    except KeyboardInterrupt:
      log.debug("Interrupt detected")
      pass
    except SystemExit:
      pass
    except Exception as e:
      log.error("Error in application: {}", e)
      log.debug(traceback.format_exc())
      pass
    return True

  def run_help(self, ns):
    try:
      ns.Application(['-h'], True, self.state).run()
    except SystemExit:
      pass
    return True

  #
  # Begin commands
  #

  def help_edts(self):
    return self.run_help(edts)

  def do_edts(self, args):
    return self.run_application(edts, args)

  def help_direction(self):
    return self.run_help(direction)

  def do_direction(self, args):
    return self.run_application(direction, args)

  def help_distance(self):
    return self.run_help(distance)

  def do_distance(self, args):
    return self.run_application(distance, args)

  def help_raikogram(self):
    return self.help_distance()

  def do_raikogram(self, args):
    return self.do_distance(args)

  def help_close_to(self):
    return self.run_help(close_to)

  def do_close_to(self, args):
    return self.run_application(close_to, args)

  def help_coords(self):
    return self.run_help(coords)

  def do_coords(self, args):
    return self.run_application(coords, args)

  def help_find(self):
    return self.run_help(find)

  def do_find(self, args):
    return self.run_application(find, args)

  def help_galmath(self):
    return self.run_help(galmath)

  def do_galmath(self, args):
    return self.run_application(galmath, args)

  def help_fuel_usage(self):
    return self.run_help(fuel_usage)

  def do_fuel_usage(self, args):
    return self.run_application(fuel_usage, args)

  def help_starcache(self):
    return self.run_help(vsc)

  def do_starcache(self, args):
    return self.run_application(vsc, args)

  def help_vsc(self):
    return self.run_help(vsc)

  def do_vsc(self, args):
    return self.run_application(vsc, args)

  def help_set_verbosity(self):
    print("usage: set_verbosity N")
    print("")
    print("Set log level (0-3)")
    return True

  def do_set_verbosity(self, args):
    env.set_verbosity(int(args))
    return True

  def help_load_ship(self):
    print("usage: load_ship coriolis_file")
    print("")
    print("Read a Coriolis ship dump")
    return True

  def do_load_ship(self, args):
    ap = argparse.ArgumentParser(fromfile_prefix_chars="@", prog = "read_ship")
    ap.add_argument("filename", type=str)
    try:
      argobj = ap.parse_args(shlex.split(args))
    except SystemExit:
      return True
    s = ship.Ship.from_file(argobj.filename)
    self.state['ship'] = s

    print("")
    print(str(s))
    print("")

    return True

  def help_set_ship(self):
    print("usage: set_ship -m N -t N -f NC [-c N]")
    print("")
    print("Set the current ship to be used in other commands")
    return True

  def do_set_ship(self, args):
    ap = argparse.ArgumentParser(fromfile_prefix_chars="@", prog = "set_ship")
    ap.add_argument("-f", "--fsd", type=str, required=True, help="The ship's frame shift drive in the form 'A6 or '6A'")
    ap.add_argument("-m", "--mass", type=float, required=True, help="The ship's unladen mass excluding fuel")
    ap.add_argument("-t", "--tank", type=float, required=True, help="The ship's fuel tank size")
    ap.add_argument("-c", "--cargo", type=int, default=0, help="The ship's cargo capacity")
    ap.add_argument(      "--fsd-optmass", type=str, help="The optimal mass of your FSD, either as a number in T or modified percentage value (including %% sign)")
    ap.add_argument(      "--fsd-mass", type=str, help="The mass of your FSD, either as a number in T or modified percentage value (including %% sign)")
    ap.add_argument(      "--fsd-maxfuel", type=str, help="The max fuel per jump of your FSD, either as a number in T or modified percentage value (including %% sign)")
    try:
      argobj = ap.parse_args(shlex.split(args))
    except SystemExit:
      return True
    s = ship.Ship(argobj.fsd, argobj.mass, argobj.tank, argobj.cargo)
    if argobj.fsd_optmass is not None or argobj.fsd_mass is not None or argobj.fsd_maxfuel is not None:
      fsd_optmass = util.parse_number_or_add_percentage(argobj.fsd_optmass, s.fsd.stock_optmass)
      fsd_mass = util.parse_number_or_add_percentage(argobj.fsd_mass, s.fsd.stock_mass)
      fsd_maxfuel = util.parse_number_or_add_percentage(argobj.fsd_maxfuel, s.fsd.stock_maxfuel)
      s = s.get_modified(optmass=fsd_optmass, fsdmass=fsd_mass, maxfuel=fsd_maxfuel)
    self.state['ship'] = s

    print("")
    print(str(s))
    print("")

    return True

  def help_ship(self):
    print("Show the current ship")
    return True

  def do_ship(self, args):
    if 'ship' in self.state:
      print(str(self.state['ship']))
    else:
      print("No saved ship")
    return True

  def help_quit(self):
    print("Exit this shell by typing \"exit\", \"quit\" or Control-D.")
    return True

  def do_quit(self, args):
    return False

  def help_exit(self):
    return self.help_quit()

  def do_exit(self, args):
    return False

  #
  # End commands
  #

  def do_EOF(self, args):
    print()
    return False

  def precmd(self, line):
    self.start_time = time.time()
    return line

  def postcmd(self, retval, line):
    if retval is False:
      return True
    log.debug("Command complete, time taken: {0:.4f}s", time.time() - self.start_time)

  # Prevent EOF showing up in the list of commands
  def print_topics(self, header, cmds, cmdlen, maxcol):
    if cmds:
      cmds = [c for c in cmds if c != "EOF"]
      cmd.Cmd.print_topics(self, header, cmds, cmdlen, maxcol)

if __name__ == '__main__':
  env.start()
  EDI().cmdloop()
  env.stop()
