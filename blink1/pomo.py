#! /usr/bin/python

"""Controls a blink1 via the blink1-tool commandline.

Displays green until you press enter to begin a pomodoro. During a pomodoro,
the display is red with periodic pulses to hint at how much time remains. The
shorter the pulse, the less time remains. When less than 5 minutes remain, the
pulses are yellow instead of black, mirroring the European traffic lights which
are red+yellow before becoming green.

Whenever the screensaver is enabled, the display goes to blue and slowly fades
to black, giving a hint as to how long ago you were last at your desk.
"""
__author__ = 'Sean Fellows'

import argparse
from datetime import datetime
from datetime import timedelta
import sys
import select
import subprocess
import time

parser = argparse.ArgumentParser(description='Controls a blink1 via the blink1-tool commandline.')
parser.add_argument('--device_num', type=str, help='which blink1 to control, or "all"')
args = parser.parse_args()

POMODORO_DURATION = timedelta(minutes=30)
SCREENSAVER_FADE_DURATION = timedelta(minutes=10)

# Holy hacks batman...
screensaver_time = None

def doit(blink1_args, check_screensaver=True, debug_screensaver=False):
  global args
  if check_screensaver and off_when_screensaver(debug_screensaver):
    return
  subprocess.call(['./blink1-tool -d %s ' % args.device_num + blink1_args] , shell=True)

def off_when_screensaver(debug_screensaver):
  global screensaver_time
  if (not subprocess.call(['ps -e | grep \'ScreenSaverEngine\|LockScreen\' | grep -v grep'] , shell=True) or
      subprocess.call(['ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler | grep CurrentPowerState\\"=4'] , shell=True)):
    if not screensaver_time:
      screensaver_time = datetime.now()
    v = 255 - int(255.0 * (datetime.now() - screensaver_time).total_seconds() / SCREENSAVER_FADE_DURATION.total_seconds())
    if v < 0:
      print 'screensaving --off'
      doit('--off', check_screensaver=False)
    else:
      print 'screensaving %s' % v
      doit('--hsb 180,255,%s' % v, check_screensaver=False)
    return True
  elif debug_screensaver:
    print 'screensaving disabled'
    subprocess.call(['ioreg -w 0 -c IODisplayWrangler -r IODisplayWrangler'] , shell=True)
  screensaver_time = None
  return False


while True:
  doit('--green')
  ins = select.select( [sys.stdin], [], [], 3 )
  if not any(ins):
    continue
  sys.stdin.readline()
  
  start = datetime.now()
  finish = start + POMODORO_DURATION
  i = 0
  while datetime.now() < finish:
    i += 1
    doit('--red')
    to_go = finish - datetime.now()
    print 'pomodor %s' % to_go
    speed = int(1500 * (to_go).total_seconds() / POMODORO_DURATION.total_seconds())
    if speed > 0 and (to_go <= timedelta(minutes=1) or not i % 3):
      if speed < 300:
        speed = 300
      #print 'fancy speed %s' % speed
      if to_go < timedelta(minutes=5):
        doit('--yellow -m %s' % speed)
      else:
        doit('--off -m %s' % speed)
      time.sleep(speed / 1000.0)
      doit('--red -m %s' % speed)
      time.sleep(speed / 1000.0)
    else:
      time.sleep(1)