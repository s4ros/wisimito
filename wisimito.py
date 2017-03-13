import os
import time
import sys
import subprocess

###############################################################################
## WisiMiTo (c) 2017 by s4ros
### simple nearest wifi observer

#########
# TODO:
# - parametrize with sys.argv[]

class c:
    head = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    warn = '\033[93m'
    fail = '\033[91m'
    e = '\033[0m'
    b = '\033[1m'
    u = '\033[4m'

# -----------------------------------------------------------------------
def check_user_permissions():
  """
    Checks if script has root privileges
  """
  if os.geteuid() != 0:
    print "Sorry, you need root privileges."
    sys.exit(1)
  return 0

# -----------------------------------------------------------------------
def get_iwlist_scan():
  """
  Returns output list of executing iwlist scanning subprocess
  """
  cmd = subprocess.Popen(["iwlist", "wlx74ea3a896226", "scanning"], stdout=subprocess.PIPE).communicate()[0].lstrip(" ").split("Cell")
  output = []
  for el in cmd:
    new_element = el.split("\n")
    output.append(new_element)
  return output

# -----------------------------------------------------------------------
def get_wifi_data():
  """
  Returns a list stripped out of Spaces supplied by iwlist scanning
  """
  output = []
  for el in get_iwlist_scan():
    new_list = []
    for e in el:
      new_list.append(e.lstrip())
    output.append(new_list)
  return output

# -----------------------------------------------------------------------
def calculate_quality(quality):
  """
  Returns % value representation of Wifi's signal quality
  """
  return (int(quality)/70.0) * 100

# -----------------------------------------------------------------------
def return_dict_data(wifi):
  """
  Returns a dictionary by parsing the stripped iwlist scanning subprocess
  """
  search_for = [ "Quality", "ESSID", "Channel", "Address" ]
  output = dict()
  finale = []

  for el in wifi:
    if len(wifi) < 3:
      continue
    if "Address" in el:
      output['mac'] = el.split(' ')[3]
    elif "Quality" in el:
      tmp = el.split(' ')
      output['quality'] = calculate_quality(tmp[0].split('=')[1].split("/")[0])
      output['signal'] = tmp[3].split('=')[1]+' dBm'
    elif "ESSID" in el:
      output['ssid'] = el.split(':')[1].split('"')[1]
  return output

# -----------------------------------------------------------------------
def build_wifi():
  """
  Returns the whole dictionary with informations about sorrounding wifi networks
  """
  data = get_wifi_data()
  output = []
  for el in data:
    tmp = return_dict_data(el)
    if tmp:
      output.append(return_dict_data(el))
  return output

# -----------------------------------------------------------------------
def sort_by_quality(wifi):
  sortedl = wifi
  for i in range(len(sortedl)):
    for j in range(len(sortedl)-1):
      if sortedl[j+1]['quality'] > sortedl[j]['quality']:
        sortedl[j+1], sortedl[j] = sortedl[j], sortedl[j+1]
  return sortedl
# -----------------------------------------------------------------------
def print_wifi_clean(wifi):
  print "[%3.0f%%] WiFi SSID: %25s,\t(signal: %s)" % (wifi['quality'], wifi['ssid'], wifi['signal'])
# -----------------------------------------------------------------------

def print_wifi(wifi):
  # tp - ToPrint
  tp =  c.b +"[" + c.e
  ## quality
  if wifi['quality'] > 75:
    tp += c.green
    ssid = c.green + c.b + "%25s" % wifi['ssid'] + c.e
  elif wifi['quality'] <= 75 and wifi['quality'] > 50:
    tp += c.blue
    ssid = c.blue + c.b + "%25s" % wifi['ssid'] + c.e
  elif wifi['quality'] <= 50 and wifi['quality'] > 25:
    tp += c.warn
    ssid = c.warn + c.b + "%25s" % wifi['ssid'] + c.e
  else:
    tp += c.fail
    ssid = c.fail + c.b + "%25s" % wifi['ssid'] + c.e
  tp += "%3.0f" % (wifi['quality']) + c.b + "]" + c.e
  ## network ssid
  tp += c.head + " WiFi SSID: " + c.e + ssid + ",\t"
  ## signal
  tp += c.b + "(" + c.e + c.u + "%s"%wifi['signal'] + c.e + c.b + ")" + c.e
  print tp
# -----------------------------------------------------------------------
## ** main() ** ##
if __name__ == "__main__":

  while True:
    check_user_permissions()
    wifi = sort_by_quality(build_wifi())
    for el in wifi:
      print_wifi_clean(el)
    time.sleep(1)
    os.system("clear")
