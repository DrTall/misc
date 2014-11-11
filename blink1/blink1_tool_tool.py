#! /usr/bin/python

"""A tool to control the blink1-tool. Life is suffering."""
__author__ = 'Sean Fellows'

from datetime import datetime
from datetime import timedelta
import subprocess

SCREENSAVER_FADE_DURATION = timedelta(minutes=10)

def set_blink1(blink1_args, device_num, check_screensaver=True, debug_screensaver=False):
  if check_screensaver and off_when_screensaver(device_num, debug_screensaver):
    return
  subprocess.call(['./blink1-tool -d %s ' % device_num + blink1_args] , shell=True)

def off_when_screensaver(device_num, debug_screensaver):
  global screensaver_time
  if (not subprocess.call(['ps -e | grep \'ScreenSaverEngine\|LockScreen\' | grep -v grep'] , shell=True) or
      subprocess.call(['ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler | grep CurrentPowerState\\"=4'] , shell=True)):
    if not screensaver_time:
      screensaver_time = datetime.now()
    v = 255 - int(255.0 * (datetime.now() - screensaver_time).total_seconds() / SCREENSAVER_FADE_DURATION.total_seconds())
    if v < 0:
      print 'screensaving --off'
      set_blink1('--off', device_num, check_screensaver=False)
    else:
      print 'screensaving %s' % v
      set_blink1('--hsb 180,255,%s' % v, device_num, check_screensaver=False)
    return True
  elif debug_screensaver:
    print 'screensaving disabled'
    subprocess.call(['ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler'] , shell=True)
  screensaver_time = None
  return False