import defs
import logging
import platform
import re
import ssl
import sys

if sys.version_info >= (3, 0):
  import urllib.request
else:
  import urllib2

log = logging.getLogger("util")

USER_AGENT = '{}/{}'.format(defs.name, defs.version)

# Match a float such as "33", "-33", "-33.1"
_rgxstr_float = r'[-+]?\d+(?:\.\d+)?'
# Match a set of coords such as "[33, -45.6, 78.910]"
_rgxstr_coords = r'^\[\s*(?P<x>{0})\s*[,/]\s*(?P<y>{0})\s*[,/]\s*(?P<z>{0})\s*\](?:=(?P<name>.+))?$'.format(_rgxstr_float)
# Compile the regex for faster execution later
_regex_coords = re.compile(_rgxstr_coords)

def parse_coords(sysname):
  rx_match = _regex_coords.match(sysname)
  if rx_match is not None:
    # If it matches, make a fake system and station at those coordinates
    try:
      cx = float(rx_match.group('x'))
      cy = float(rx_match.group('y'))
      cz = float(rx_match.group('z'))
      name = rx_match.group('name') if rx_match.group('name') is not None else sysname
      return (cx, cy, cz, name)
    except Exception as ex:
      log.debug("Failed to parse manual system: {}".format(ex))
  return None


def open_url(url):
  if sys.version_info >= (3, 0):
    # Specify our own user agent as Cloudflare doesn't seem to like the urllib one
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
      return urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
      log.error("Error {0} opening {1}: {2}".format(err.code, url, err.reason))
      return None
  else:
    sslctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    # If we're on OSX with OpenSSL 0.9.x, manually specify preferred ciphers so CloudFlare can negotiate successfully
    if platform.system() == 'Darwin' and ssl.OPENSSL_VERSION_INFO[0] < 1:
      sslctx.set_ciphers("ECCdraft:HIGH:!aNULL")
    # Specify our own user agent as Cloudflare doesn't seem to like the urllib one
    request = urllib2.Request(url, headers={'User-Agent': USER_AGENT})
    try:
      return urllib2.urlopen(request, context=sslctx)
    except urllib2.HTTPError as err:
      log.error("Error {0} opening {1}: {2}".format(err.code, url, err.reason))
      return None

def read_stream_line(stream):
  if sys.version_info >= (3, 0):
    return stream.readline().decode("utf-8")
  else:
    return stream.readline()

def read_stream(stream, limit = None):
  if sys.version_info >= (3, 0):
    return stream.read(limit).decode("utf-8")
  else:
    return stream.read(-1 if limit is None else limit)

def read_from_url(url):
  return read_stream(open_url(url))


def is_interactive():
  return hasattr(sys, 'ps1')


def is_str(s):
  if sys.version_info >= (3, 0):
    return isinstance(s, str)
  else:
    return isinstance(s, basestring)


def download_file(url, file):
  if sys.version_info >= (3, 0):
    urllib.request.urlretrieve(url, file)
  else:
    urllib2.urlretrieve(url, file)


def string_bool(s):
  return s.lower() in ("yes", "true", "1")


def unpack_and_shift(value, bits):
  return (value >> bits, value & (2**bits-1))

def pack_and_shift(value, new_data, bits):
  return (value << bits) + (new_data & (2**bits-1))
