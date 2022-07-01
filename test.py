from collections import namedtuple

test = namedtuple('Command', ["lesson", "date"])
test1 = namedtuple("Command", ["lesson"])
a = test("str", 33)
print(isinstance(a, test))
