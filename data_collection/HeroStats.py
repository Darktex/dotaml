__author__ = 'davide'
from pymongo import MongoClient
from progressbar import ProgressBar, Bar, Percentage, ETA
import numpy as np

np.set_printoptions(threshold=np.nan)

client = MongoClient()
db = client.dotabot
matches = db.matches
heroes_stats = db.heroes_stats

# We're going to iterate through all the matches and
# collect interesting hero-related statistics.
# In particular, we are interested in the following fields:
#
#   - tower_damage
#   - hero_damage
#   - kills
#   - deaths
#   - hero_healing
#   - gold_per_min
#   - level
#   - xp_per_min
#   - last_hits
#   - denies

NUM_HEROES = 108  # Still ok as a number as of May 2014

# This is how the table is initialized:

#for hero_id in range(1, NUM_HEROES):
#    hero_stats = {
#        '_id'       : 1,
#        'matches'   : []
#    }
#    heroes_stats.insert(hero_stats)

# Our training label vector, Y, is a bit vector indicating
# whether radiant won (1) or lost (-1)

NUM_MATCHES = matches.count()

widgets = ['Working...', ETA(), Percentage(), ' ', Bar()]
pbar = ProgressBar(widgets=widgets, maxval=NUM_MATCHES).start()

for i, record in enumerate(matches.find()):
    pbar.update(i)
    players = record['players']
    length = record['duration']
    for player in players:
        # Logs only record if radiant win or lose. So to find out if the player won,
        # we check if he is radiant (I would have expected to just check the place in the players[] array,
        # but apparently you must check the field player['player_slot'] which is < 128 iff the player
        # is on Radiant). In that case, his outcome is the same as the radiant.
        # Otherwise, it's the opposite.

        game_won = record['radiant_win'] if player['player_slot'] < 128 else not (record['radiant_win'])
        hero_id = player['hero_id'] - 1

        match_stats = {
            "tower_damage": player['tower_damage'],
            "hero_damage": player['hero_damage'],
            "kills": player['kills'],
            "deaths": player['deaths'],
            "hero_healing": player['hero_healing'],
            "gold_per_min": player['gold_per_min'],
            "level": player['level'],
            "xp_per_min": player['xp_per_min'],
            "last_hits": player['last_hits'],
            "denies": player['denies'],
            "match_length": length,
            "game_won": game_won
        }

        heroes_stats.update({'_id': hero_id}, {'$push': {'matches': match_stats}})

pbar.finish()

