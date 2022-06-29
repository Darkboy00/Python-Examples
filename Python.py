# Numbers and Strings 

"""
a = 9
b = 10
print(a * b)
print("Hello World")
print(91)
"""

# Strings

"""
print("a" + "b")
print("a"*3)
"""

# String Methods - len() 

"""
h = "Hello World"
print(len(h))
print(len("Hello World"))
"""

# String Methods - upper() & lower()

"""
h = "hello"
print(h.upper())
print(h.lower())
print(h.islower())

H = h.upper()
print(H.isupper())
print(H.islower())
"""

# String Methods - replace()

"""
h = "hello"
print(h.replace("e","a"))
"""

# String Methods - strip()

"""
h = " hello "
print(h.strip())
h = "-hello-"
print(h.strip("-"))
"""

# Methods 

"""
h = "hello world"
print(dir(h))
print(h.capitalize())
print(h.title())
"""

# Substrings

"""
h = "hello world"
print(h[0])
print(h[0:6])
"""

# Variables

"""
a = 9
b = "hello"
c = a * 2

print(a/c)
print(a*c)
print(a*3)

print(type(2))
print(type(100.2))
print(type(1+2j))
"""

# Type Conversions

"""
a = int(input())
b = int(input())

print(type(a))
print(a + b)
print(int(11.0))
print(float(11))
print(type(str(12)))
"""

# print()

"""
print("hello world")
print("hello","world")
print("hello","world", sep = "_")
"""

# Data Structures
# Lists - [] & list()

"""
a = [10, 20, 30, 40]
print(type(a))

b = ["a", 20, 20.2, a]
print(len(b))

print(a[0])
print(type(a[0]))

c = [a, b]
print(c)
"""

# Lists - Element operations

"""
list1 = [10, 20, 30, 40, 50, 60]

print(list1[0])
print(list1[0:2])
print(list1[:2])
print(list1[2:])

list2 = ["a", 20, [30, 40, 50, 60]]

print(list2[2])
print(list2[0:2])
print(list2[2][1])
"""

# Lists - Element replacement

"""
list1 = ["mehmet","selim","süleyman","osman","orhan"]
list1[1] = "yavuz"
print(list1)

list1[0:3] = "fatih","yavuz","kanuni"
print(list1)

list1 = list1 + ["bayezid"]
print(list1)

del list1[0]
print(list1)
"""

# Lists - append & remove 

"""
list1 = ["osman","orhan","murat","bayezid","mehmet"]
list1.append("selim")
print(list1)
list1.remove("selim")
print(list1)
"""

# Lists - insert & pop 

"""
list1 = ["osman","orhan","murat"]
list1.insert(3,"süleyman")
print(list1)
list1.insert(len(list1),"selim")
print(list1)
list1.pop(0)
print(list1)
"""

# Lists - count 

"""
list1 = ["osman","orhan","murat","osman"]
print(list1.count("orhan"))
print(list1.count("osman"))
"""

# Lists - copy

"""
list1 = ["osman","orhan","murat","osman"]
list2 = list1.copy()
print(list2)
"""

# Lists - extend

"""
list1 = ["osman","orhan","murat","osman"]
list1.extend(["kanuni","yavuz"])
print(list1)
"""

# Lists - index()

"""
list1 = ["osman","orhan","murat","osman"]
print(list1.index("murat"))
"""

# Lists - reverse()

"""
list1 = ["osman","orhan","murat","kanuni"]
list1.reverse()
print(list1)
"""

# Lists - sort()

"""
list1 = [10,20,3,90]
list1.sort()
print(list1)
"""

# Lists - clear()

"""
list1 = [10,20,3,90]
list1.clear()
print(list1)
"""

# Data Structures - tuple()

"""

t = ("mehmet", "kanuni", 1, 3.5, [1, 2, 3])
t = "mehmet", "kanuni", 1, 3.5, [1, 2, 3]
t = ("mehmet",)
print(type(t))

t = "mehmet", "kanuni", 1, 3.5, [1, 2, 3]
print(t[1])
"""

# Data Structures - dictionary

"""
cars = {"car1":10000, "car2":20000, "car3":30000}
cars = {"car1":"bmw", "car2":"audi", "car3":"fiat"}

print(len(cars))
print(cars)
print(cars["car2"])

cars = {"car1":{"car1":10000, "car2":20000, "car3":30000}, "car2":{"car1":10000, "car2":20000, "car3":30000}, "car3":{"car1":10000, "car2":20000, "car3":30000}}

print(cars["car2"]["car1"])

cars = {"car1":"bmw", "car2":"audi", "car3":"fiat"}
cars["car4"] = "mercedes"
print(cars)

cars["car1"] = "tesla"
print(cars)

t = ("tuple",)
cars[t] = "tuple"
print(cars)
"""

# Data Structures - sets

s = set()
print(s)

l = [1,"a","ali",123]
s = set(l)
print(s)

t = ("a","mehmet")
s = set(t)
print(s)

h = "hello_world"
print(type(h))
s = set(h)
print(s)

l = ["hello","world","hello","hello"]
s = set(l)
print(s)
print(len(s))