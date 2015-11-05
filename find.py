import argparse
import env
import fnmatch
import logging
from vector3 import Vector3

app_name = "find"

log = logging.getLogger(app_name)


class Application:

  def __init__(self, arg, hosted):
    ap_parents = [env.arg_parser] if not hosted else []
    ap = argparse.ArgumentParser(description = "Find System or Station", fromfile_prefix_chars="@", parents=ap_parents, prog = app_name)
    ap.add_argument("-a", "--anagram", default=False, action='store_true', help="Find names matching an anagram of the provided string")
    ap.add_argument("-s", "--systems", default=False, action='store_true', help="Limit the search to system names")
    ap.add_argument("-t", "--stations", default=False, action='store_true', help="Limit the search to station names")
    ap.add_argument("system", metavar="system", type=str, nargs=1, help="The system or station to find")
    self.args = ap.parse_args(arg)

  def run(self):

    searchname = self.args.system[0].lower()

    sys_matches = []
    stn_matches = []

    if not self.args.anagram:
      if self.args.systems or not self.args.stations:
        sys_matches = fnmatch.filter(env.eddb_systems_by_name.keys(), searchname)
      if self.args.stations or not self.args.systems:
        stn_matches = fnmatch.filter(env.eddb_stations_by_name.keys(), searchname)

    else:
      if self.args.systems or not self.args.stations:
        sys_matches = self.anagram_find_matches(env.eddb_systems_by_name.keys(), searchname)
      if self.args.stations or not self.args.systems:
        stn_matches = self.anagram_find_matches(env.eddb_stations_by_name.keys(), searchname)

    if (self.args.systems or not self.args.stations) and len(sys_matches) > 0:
      print ""
      print "Matching systems:"
      print ""
      for sys in sys_matches:
        stn = env.get_station(sys, None, True)
        print "  " + stn.to_string()
      print ""

    if (self.args.systems or not self.args.stations) and len(stn_matches) > 0:
      print ""
      print "Matching stations:"
      print ""
      for stn_name in stn_matches:
        stns = env.eddb_stations_by_name[stn_name]
        for stn in stns:
          stn_obj = env.get_station(env.eddb_systems_by_id[stn["system_id"]]["name"], stn["name"], True)
          print "  " + stn_obj.to_string()
      print ""

    if len(sys_matches) == 0 and len(stn_matches) == 0:
      print ""
      print "No matches"
      print ""

    return True


  def anagram_find_matches(self, keys, query):
    results = []
    for line in keys:
      for key in line.split(' '):
        passed = True
        for ch in query:
          log.debug("ch = {0}".format(ch))
          if ch >= 'a' and ch <= 'z' and not ch in key:
            log.debug("passed = false")
            passed = False
            break
        if passed == True:
          results.append(line)
    return results


if __name__ == '__main__':
  a = Application(env.local_args, False)
  a.run()
