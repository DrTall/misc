#!/usr/bin/python

"""Polls IFTTT for blink1 events and reacts to them.

Skeleton based on https://gist.github.com/tomconte/4496283
"""

import argparse
import collections
import datetime
import functools
import urllib2
import json
import time
import subprocess

import blink1_tool_tool
 
parser = argparse.ArgumentParser(description='Controls a blink1 via the blink1-tool commandline.')
parser.add_argument('--device_num', type=str, help='which blink1 to control, or "all"')
parser.add_argument('--api_key', type=str, help='which blink1 to poll from IFTTT"', required=True)
args = parser.parse_args()

POLL_SEC = 5
set_blink1 = functools.partial(blink1_tool_tool.set_blink1, device_num=args.device_num, check_screensaver=False)

# Holy unsafe url construction batman!
url = 'http://api.thingm.com/blink1/events/%s' % args.api_key
 
last_time = datetime.datetime(1900,1,1,1)

PatternStepT = collections.namedtuple('PatternStep', ['rgb', 'time', 'side', 'hold_time', 'hsv'])
def PatternStep(rgb, time, side=0, hold_time=0, hsv=None):
  return PatternStepT(rgb, time, side, hold_time, hsv)

Pattern = collections.namedtuple('Pattern', ['repeats', 'steps'])

interval = 100
POLICE = Pattern(6, [
  PatternStep('FF0000', interval, 1),
  PatternStep('0000FF', interval, 2),
  PatternStep('0000FF', interval, 1),
  PatternStep('FF0000', interval, 2),
])
interval = 300
BLUE = Pattern(3, [
  PatternStep('0000FF', interval, 0, interval),
  PatternStep('000000', interval, 0, interval),
])
interval = 300
BLUE_GREEN = Pattern(3, [
  PatternStep('0000FF', interval, 0, interval),
  PatternStep('00FF00', interval, 0, interval),
])
interval = 300
BLUE_ORANGE = Pattern(3, [
  PatternStep('0000FF', interval, 0, interval),
  PatternStep('ff8c00', interval, 0, interval),
])
interval = 300
RED = Pattern(3, [
  PatternStep('FF0000', interval, 0, interval),
  PatternStep('000000', interval, 0, interval),
])

interval = 200
HEART = Pattern(4, [
  PatternStep('ff1493', interval),
  PatternStep('ff69b4', interval, 2),
  PatternStep('b03060', interval, 1),
  PatternStep('ff1493', interval),
  PatternStep('ff69b4', interval, 1),
  PatternStep('b03060', interval, 2),
  PatternStep('ff1493', interval),
])

interval = 50
ORANGE_STROBE = Pattern(20, [
  PatternStep('ff8c00', interval, 0, interval),
  PatternStep('000000', interval, 0, interval),
])

def run_pattern(pattern, custom_repeats=0):
  for _ in range(custom_repeats or pattern.repeats):
    for step in pattern.steps:
      set_blink1('-m %s --rgb %s -l %s' % (step.time, step.rgb, step.side))
      time.sleep((step.time + step.hold_time) / 1000.0)
  set_blink1('-m 500 --off')
  

def handle_event(name):
  if name.startswith('Gmail'):
    _, email, subject = (name.split(' ', 2) + [""]*3)[:3]
    run_pattern({
      'ship-confirm@amazon.com': BLUE_GREEN,
      'fello3@gmail.com': BLUE_ORANGE,
      'jordpenn@gmail.com': HEART,
      'jordanpfellows@gmail.com': HEART,
      'markpenn7@gmail.com': POLICE,
    }.get(email, BLUE))
  elif name.startswith('missed-phone-call'):
    _, contact = (name.split(' ', 1) + [""]*3)[:2]
    run_pattern(POLICE)
  elif name.startswith('Google Calendar'):
    _, _, title = (name.split(' ', 2) + [""]*3)[:3]
    run_pattern(RED, custom_repeats=10)
  else:
    run_pattern(POLICE)
  
 
while True:
  try:
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    data = res.read()
   
    ev = json.loads(data)
  except:
    time.sleep(10 * POLL_SEC)
    continue
 
  if ev['event_count'] > 0:
    for e in ev['events']:
      event_time = datetime.datetime.fromtimestamp(int(e['date']))
      print 'Found an event at time: %s' % event_time
      if event_time > last_time:
        print 'trigger: ' + e['name']
        handle_event(e['name'])

  now = datetime.datetime.now()
  if last_time.minute < 50 and now.minute >= 50 and now.hour > 16 and now.hour < 21:
    run_pattern(ORANGE_STROBE)
  last_time = now
  print 'sleeping...'
  time.sleep(POLL_SEC)