#! /usr/bin/python

import collections, itertools, random

Card = collections.namedtuple('Card', ['rank', 'suit'])

# make a deck of cards
deck = list(itertools.product(range(2,15),['s','h','d','c']))
deck = [Card(*a) for a in deck]

def name(c):
  rank_names = {10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
  rank_names.update({i:i for i in range(10)})
  return '%s%s' % (rank_names[c.rank],c.suit)

def score(h):
  rank_scores = {10: 10, 11: 10, 12: 10, 13: 10, 14: 11}
  rank_scores.update({i:i for i in range(10)})
  assert len(h) == 3
  suit_sums = collections.defaultdict(int)
  for c in h:
    suit_sums[c.suit] += rank_scores[c.rank]
  #print '%s = %s = %s' % ([name(c) for c in h], suit_sums, max(suit_sums.values()))
  return max(suit_sums.values())

score_counts = collections.defaultdict(int)
NUM_TRIALS = 1000000
for sim_num in range(NUM_TRIALS):
  random.shuffle(deck)
  score_counts[score(deck[:3])] += 1

cum_score = 0
for s,n in sorted(score_counts.iteritems()):
  cum_score += n
  print '%02d: %.1f' % (s ,100.0 * cum_score / NUM_TRIALS)