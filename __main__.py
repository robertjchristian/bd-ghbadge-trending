from bitdeli.chain import Profiles
import random

def repos(profiles):
    repos = {}
    for profile in profiles:
        for repo in profile['repos']:
            repos[repo] = random.randint(0, 3)
    yield [{'repo': repo, 'badge': 'trending-badge%d.png' % t}
           for repo, t in repos.items() + [('!default', 0)]]
    
Profiles().map(repos).show('table',
                           id='repos',
                           size=(12, 6),
                           json_export=True)
        
    
