import itertools as iter

group = 'a', 'b', 'c'
group_b = 'd', 'e', 'g'

mapped = list(iter.product(group, group_b))

print(mapped)