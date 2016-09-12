#!/usr/bin/env python

import sys
import bottle
import json
import collections

sys.path.insert(0, '..')
import env
import pgnames
import pgdata
import sector
import vector3
del sys.path[0]


def vec3_to_dict(v):
  return collections.OrderedDict([('x', v.x), ('y', v.y), ('z', v.z)])


@bottle.hook('before_request')
def strip_path():
  bottle.request.environ['PATH_INFO'] = bottle.request.environ['PATH_INFO'].rstrip('/')


@bottle.route('/')
def index():
  return bottle.template('index')


@bottle.route('/api/v1')
def api_index():
  return bottle.template('api_v1_index')


@bottle.route('/static/<path:path>')
def static(path):
  return bottle.static_file(path, root='static')


@bottle.route('/api/v1/system_name/<x:float>,<y:float>,<z:float>/<mcode:re:[a-h]>')
def api_system_name(x, y, z, mcode):
  pos = vector3.Vector3(x, y, z)
  syst = pgnames.get_system(pos, mcode)
  result = {'position': vec3_to_dict(pos), 'names': []}

  if syst is not None:
    result['names'] += [{'name': syst.name, 'type': syst.sector.sector_class}]
  else:
    bottle.response.status = 400
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}


@bottle.route('/api/v1/sector_name/<x:float>,<y:float>,<z:float>')
def api_sector_name(x, y, z):
  v = vector3.Vector3(x, y, z)
  result = {'names': [], 'position': vec3_to_dict(v)}
  sect = pgnames.get_sector(v, allow_ha=True)
  if sect is not None and isinstance(sect, sector.HASector):
    result['names'].append({'name': sect.name, 'type': sect.sector_class})
    sect = pgnames.get_sector(v, allow_ha=False)
  if sect is not None:
    result['names'] += [{'name': sect.name, 'type': sect.sector_class}]
  if not any(result['names']):
    bottle.response.status = 400
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}


@bottle.route('/api/v1/system_position/<name>')
def api_system_position(name):
  syst = pgnames.get_system(name)
  if syst is not None:
    result = {'name': pgnames.get_canonical_name(name), 'position': vec3_to_dict(syst.position), 'uncertainty': syst.uncertainty}
  else:
    bottle.response.status = 400
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}


@bottle.route('/api/v1/sector_position/<name>')
def api_sector_position(name):
  sect = pgnames.get_sector(name)
  if sect is not None:
    if isinstance(sect, sector.HASector):
      result = {'name': pgnames.get_canonical_name(name), 'type': 'ha', 'centre': vec3_to_dict(sect.centre), 'radius': sect.radius}
    else:
      result = {'name': pgnames.get_canonical_name(name), 'type': 'pg', 'origin': vec3_to_dict(sect.origin), 'centre': vec3_to_dict(sect.centre), 'size': sect.size}
  else:
    bottle.response.status = 400
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}

@bottle.route('/api/v1/system/<name>')
def api_system(name):
  with env.use() as data:
    syst = data.get_system(name, keep_data=True)
    if syst is not None:
      result = syst.data
  bottle.response.content_type = 'application/json'
  return {'result': result}

@bottle.route('/api/v1/system/<name>/stations')
def api_system_stations(name):
  result = []
  with env.use() as data:
    syst = data.get_system(name, keep_data=True)
    if syst is not None:
      for stat in data.get_stations(syst, keep_station_data=True):
        if stat is not None:
          result.append(stat.data)
  if not len(result):
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}

@bottle.route('/api/v1/system/<system_name>/station/<station_name>')
def api_system_station(system_name, station_name):
  with env.use() as data:
    stat = data.get_station(system_name, station_name, keep_data=True)
    if stat is not None:
      result = stat.data
      result['system'] = stat.system.data
    else:
      result = None
    bottle.response.content_type = 'application/json'
    return {'result': result}

@bottle.route('/api/v1/find_system/<glob>')
def api_find_system(glob):
  result = []
  with env.use() as data:
    for syst in data.find_systems_by_glob(glob, keep_data=True):
      if syst is not None:
        result.append(syst.data)
  if not len(result):
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}

@bottle.route('/api/v1/find_station/<glob>')
def api_find_station(glob):
  result = []
  with env.use() as data:
    for stat in data.find_stations_by_glob(glob, keep_data=True):
      if stat is not None:
        stndata = stat.data
        stndata['system'] = stat.system.data
        result.append(stndata)
  if not len(result):
    result = None
  bottle.response.content_type = 'application/json'
  return {'result': result}

if __name__ == '__main__':
  env.start('..')
  bottle.run(host='localhost', port=8080)
  env.stop()