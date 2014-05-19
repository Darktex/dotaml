__author__ = 'davide'
from pymongo import MongoClient
from progressbar import ProgressBar, Bar, Percentage, FormatLabel, ETA
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

#for hero_id in range(1, NUM_HEROES):
#    hero_stats = {
#        '_id'       : hero_id,
#        'matches'   : []
#    }
#    heroes_stats.insert(hero_stats)

# Our training label vector, Y, is a bit vector indicating
# whether radiant won (1) or lost (-1)

NUM_MATCHES = matches.count()

widgets = [FormatLabel('Processed: %(value)d/%(max)d matches. '), ETA(), Percentage(), ' ', Bar()]
pbar = ProgressBar(widgets=widgets, maxval=NUM_MATCHES).start()

for i, record in enumerate(matches.find()):
    pbar.update(i)
    players = record['players']
    length = record['duration']
    for player in players:

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
            "match_length": length
        }

        heroes_stats.update({'_id': hero_id}, {'$push': {'matches': match_stats}})

        # If the left-most bit of player_slot is set,
        # this player is on dire, so push the index accordingly
        player_slot = player['player_slot']
        if player_slot >= 128:
            hero_id += NUM_HEROES

        X[i, hero_id] = 1

pbar.finish()

print "Permuting, generating train and test sets."
indices = np.random.permutation(NUM_MATCHES)
test_indices = indices[0:NUM_MATCHES / 10]
train_indices = indices[NUM_MATCHES / 10:NUM_MATCHES]

X_test = X[test_indices]
Y_test = Y[test_indices]

X_train = X[train_indices]
Y_train = Y[train_indices]

print "Saving output file now..."
np.savez_compressed('test_%d.npz' % len(test_indices), X=X_test, Y=Y_test)
np.savez_compressed('train_%d.npz' % len(train_indices), X=X_train, Y=Y_train)

