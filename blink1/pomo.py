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
import functools
import sys
import select
import time

import blink1_tool_tool

parser = argparse.ArgumentParser(description='Controls a blink1 via the blink1-tool commandline.')
parser.add_argument('--device_num', type=str, help='which blink1 to control, or "all"')
args = parser.parse_args()

POMODORO_DURATION = timedelta(minutes=30)

# Holy hacks batman...
screensaver_time = None

set_blink1 = functools.partial(blink1_tool_tool.set_blink1, device_num=args.device_num)

while True:
  set_blink1('--green')
  ins = select.select( [sys.stdin], [], [], 3 )
  if not any(ins):
    continue
  sys.stdin.readline()
  
  start = datetime.now()
  finish = start + POMODORO_DURATION
  i = 0
  while datetime.now() < finish:
    i += 1
    set_blink1('--red')
    to_go = finish - datetime.now()
    print 'pomodor %s' % to_go
    speed = int(1500 * (to_go).total_seconds() / POMODORO_DURATION.total_seconds())
    if speed > 0 and (to_go <= timedelta(minutes=1) or not i % 3):
      if speed < 300:
        speed = 300
      #print 'fancy speed %s' % speed
      if to_go < timedelta(minutes=5):
        set_blink1('--yellow -m %s' % speed)
      else:
        set_blink1('--off -m %s' % speed)
      time.sleep(speed / 1000.0)
      set_blink1('--red -m %s' % speed)
      time.sleep(speed / 1000.0)
    else:
      time.sleep(1)