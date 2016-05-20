# -*- coding: utf-8 -*-

import csv, string


"""
def all_combinations():
    for max_depth in (2, 3):
        fp = open('combinations{}.csv'.format(max_depth), 'w')
        for result in combinations(max_depth=max_depth):
            fp.write(result + '\n')

def combinations(prefix='', cur_depth=0, max_depth=3):
    if cur_depth == max_depth:
        yield prefix
    else:
        for letter in string.lowercase:
            for result in combinations(prefix + letter, cur_depth+1, max_depth):
                yield result
"""

def city_combinations():
    cities = set()
    for row in csv.reader(open('world_cities.csv')):
        city = row[1]
        cities.add(city[:3].lower())
    print sorted(cities)
    writer = csv.writer(open('city_prefixes.csv', 'w'))
    for prefix in sorted(cities):
        writer.writerow([prefix])


def main():
    city_combinations()

if __name__ == '__main__':
    main()

