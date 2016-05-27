# -*- coding: utf-8 -*-

import csv, string, glob, collections


def city_combinations():
    cities = collections.defaultdict(int)
    for filename in glob.glob('[A-Z]*_locations.csv'):
        for row in csv.reader(open(filename)):
            city = row[2][:3]
            if is_ascii(city):
                cities[city.lower()] += 1

    top_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)
    print top_cities
    writer = csv.writer(open('city_prefixes.csv', 'w'))
    for prefix, count in top_cities:
        writer.writerow([prefix])


def is_ascii(s):
    for c in s:
        if ord(c) >= 128:
            return False
    return True


def counter():
    fp = open('count.txt', 'w')
    for i in xrange(10000):
        fp.write('{}\n'.format(i))


def main():
    city_combinations()
    counter()


if __name__ == '__main__':
    main()

