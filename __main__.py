from collections import Counter
from itertools import groupby
from bisect import bisect
from datetime import datetime

from bitdeli.textutil import Percent
from bitdeli.chain import Profiles
from bitdeli.widgets import Title, Description, set_theme

BADGE = 'trending_badge%d.png'
TFORMAT = '%Y-%m-%dT%H:%M:%SZ'
BASELINE_THRESHOLDS = (1e2, 1e3, 1e4)
GROWTH_THRESHOLDS = (0.05, 0.2, 0.3)
NOW = datetime.utcnow()

set_theme('space')

text = {}

def weekly_uniques(profiles):
    def weekly_visits(visits):
        for visit in reversed(visits):
            t = datetime.strptime(visit['tstamp'], TFORMAT)
            days = (NOW - t).days
            if days < 14:
                yield days / 7
            else:
                break
    for profile in profiles:
        for repo, visits in profile['repos'].items():
            for week, hits in groupby(weekly_visits(visits)):
                yield repo, week
                   
def trending(profiles):
    weekstats = (Counter(), Counter())
    for repo, week in weekly_uniques(profiles):
        weekstats[week][repo] += 1
    
    text['num_repos'] = len(weekstats[0])
    if weekstats[1]:
        text['change'] = Percent(len(weekstats[0]) - len(weekstats[1]) /
                                 float(len(weekstats[1])))
    else:
        text['change'] = Percent(0)
    
    for repo, hits in weekstats[0].iteritems():
        past_hits = weekstats[1][repo]
        if past_hits:
            growth = (hits - past_hits) / float(past_hits) 
        else:
            growth = GROWTH_THRESHOLDS[0]
        score = min(3, bisect(BASELINE_THRESHOLDS, hits) +
                       bisect(GROWTH_THRESHOLDS, growth))
        yield {'repo': repo,
               'badge': BADGE % score,
               'hits': hits,
               'past hits': past_hits,
               'growth': growth}               

def table(profiles):
    yield list(sorted(trending(profiles),
                      key=lambda x: x['hits'],
                      reverse=True)) +\
          [{'repo': '!default', 'badge': BADGE % 0}]
    
Profiles().map(table).show('table',
                           id='repos',
                           size=(12, 6),
                           json_export=True)

Title("**{num_repos}** badges installed", text)

Description("The number of badges has {change.verb} by {change} "
            "compared to the past week.", text)
    
