"""Recommendation"""

from math import sqrt

# A dictionary of movie critics and their ratings of a small
# set of movies
critics = {
    'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                  'Just My Luck': 3.0, 'Superman Returns': 3.5,
                  'You, Me and Dupree': 2.5,
                  'The Night Listener': 3.0},
    'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                     'Just My Luck': 1.5, 'Superman Returns': 5.0,
                     'The Night Listener': 3.0,
                     'You, Me and Dupree': 3.5},
    'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                         'Superman Returns': 3.5, 'The Night Listener': 4.0},
    'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                     'The Night Listener': 4.5, 'Superman Returns': 4.0,
                     'You, Me and Dupree': 2.5},
    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                     'Just My Luck': 2.0, 'Superman Returns': 3.0,
                     'The Night Listener': 3.0,
                     'You, Me and Dupree': 2.0},
    'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                      'The Night Listener': 3.0, 'Superman Returns': 5.0,
                      'You, Me and Dupree': 3.5},
    'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0,
             'Superman Returns': 4.0},
    'Ashwath': {'Snakes on a Plane': 3.5, 'Superman Returns': 2.0},
}


# Returns a distance-based similarity score for person1 and person2
def sim_distance(prefs, person1, person2):
    # Get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # If they have no rating in common, return 0
    if len(si) == 0:
        return 0

    # Add up the square of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1]
                          if item in prefs[person2]])

    return 1 / (1 + sum_of_squares)


# Returns the pearson correlation coefficient for person1 and person2
def sim_pearson(prefs, person1, person2):
    # Get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # If they have no rating in common, return 0
    if len(si) == 0:
        return 0

    n = len(si)

    # Add up all the preferences
    sum1 = sum([prefs[person1][item] for item in si])
    sum2 = sum([prefs[person2][item] for item in si])

    # Sum up the squares
    sum1_square = sum([pow(prefs[person1][item], 2) for item in si])
    sum2_square = sum([pow(prefs[person2][item], 2) for item in si])

    # Sum up the products
    product_sum = sum([prefs[person1][item] * prefs[person2][item]
                       for item in si])

    # Calculate the Pearson score
    num = product_sum - (sum1 * sum2 / n)
    den = sqrt((sum1_square - pow(sum1, 2) / n) *
               (sum2_square - pow(sum2, 2) / n))

    if den == 0:
        return 0

    return num / den


# Returns the best matches for the person from the prefs dictionary.
# Number of results and similarity function are optional params.
def top_matches(prefs, person, n=5, similarity=sim_pearson):
    scores = [(similarity(prefs, person, other), other)
              for other in prefs if other != person]

    # sort the list so the heighest scores appear at the top
    scores.sort(reverse=True)

    return scores[:n]


# Gets recommendation for a person by using a weighted average
# of every other user's rankings
def get_recommendations(prefs, person, simalirity=sim_pearson):
    totals = {}
    sim_sums = {}
    for other in prefs:
        # don't compare me to myself
        if other == person:
            continue
        sim = simalirity(prefs, person, other)

        # ignore scores of zero or lower
        if sim <= 0:
            continue
        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # sum of similarities
                sim_sums.setdefault(item, 0)
                sim_sums[item] += sim

    # create the normalized list
    rankings = [(total / sim_sums[item], item)
                for item, total in totals.items()]

    # return the sorted list
    rankings.sort(reverse=True)

    return rankings


# transform dictionary
def transform_prefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # flip item and person
            result[item][person] = prefs[person][item]

    return result


# Item similarity calculate
def calculate_similar_items(prefs, n=10):
    # create a dictionary of item showing which other items the are
    # most similar to.
    result = {}

    # invert the preference matrix to be item-centric
    item_prefs = transform_prefs(prefs)

    c = 0
    for item in item_prefs:
        # status updates for large datasets
        c += 1
        if c % 100 == 0:
            print("%d / %d" % (c, len(item_prefs)))
        # find the most similar items to this one
        scores = top_matches(item_prefs, item, n=n, similarity=sim_distance)
        result[item] = scores
        return result


if __name__ == '__main__':

    from itertools import combinations

    print("simalirity between users")
    print("=" * 100)
    users = [user for user in critics.keys()]
    print("{:20} {:20} {:20} {:20}".format(
        '', '', 'Euclidean distance', 'Pearson distance'))
    print("=" * 100)
    for person1, person2 in combinations(users, 2):
        print("{:20} {:20} {:<20} {:<20}".format(
            person1, person2,
            sim_distance(critics, person1, person2),
            sim_pearson(critics, person1, person2)))

    print()
    print()
    print("simalirity between movies")
    print("=" * 100)
    movies = [movie for movie in transform_prefs(critics).keys()]
    print("{:20} {:20} {:20} {:20}".format(
        '', '', 'Euclidean distance', 'Pearson distance'))
    print("=" * 100)
    for person1, person2 in combinations(movies, 2):
        print("{:20} {:20} {:<20} {:<20}".format(
            person1, person2,
            sim_distance(transform_prefs(critics), person1, person2),
            sim_pearson(transform_prefs(critics), person1, person2)))

    print()
    print()
    print("similar items")
    print("=" * 100)
    calculate_similar_items(critics)
