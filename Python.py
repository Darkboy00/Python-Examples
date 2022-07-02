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

"""
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

l = ["hello","world"]
s = set(l)
print(dir(s))
s.add("hi")
print(s)
s.add("mehmet")
print(s)
s.remove("hi")
print(s)
s.discard("mehmet")
print(s)

set1 = set([7,8,9])
set2 = set([5,6,7,8,9,10])
print(set1.isdisjoint(set2))
print(set1.issubset(set2))
print(set2.issuperset(set1))
"""

# Sets - difference

"""
set1 = set([1,3,5])
set2 = set([1,2,3])
print(set1.difference(set2))
print(set2.difference(set1))
print(set2.symmetric_difference(set1))
print(set1 - set2)
print(set2 - set1)
"""

# Sets - intersection & union

"""
set1 = set([1,3,5])
set2 = set([1,2,3])
print(set1.intersection(set2))
print(set2.intersection(set1))
print(set1.union(set2))
set1.intersection_update(set2)
print(set1)
"""

# Functions

"""
def square_take(x):
    print("Entered number:" + str(x) + " Square:" + str(x**2))
square_take(4)

def multiply_do(x, y = 1):
    return (x * y)
print(multiply_do(3,4))
print(multiply_do(y = 3, x = 4))
print(multiply_do(3,4) * 3)

x = 3
y = 5

def addition(x, y):
    print(x + y)

addition(10,20)

x = []

def add_element(y):
    x.append(y)
add_element("mehmet")
add_element("selim")
print(x)
"""

# True-False

"""
limit = 500
print(limit == 300)
print(limit == 500)
print(3 == 5)
print(3 == 3)
"""

# if

"""
limit = 50000
income = 40000

if(income < limit):
    print("Income is smaller than the limit")
if(income > limit):
    print("Income is bigger than the limit")
"""

# else

"""
limit = 50000
income = 40000

if(income > limit):
    print("Income is bigger than the limit")
else:
    print("Income is smaller than the limit")

if(income == limit):
    print("equal")
else:
    print("not equal")
"""

# elif

"""
limit = 30000
income = 40000

if(income > limit):
    print("Income is bigger than the limit")
elif(income < limit):
    print("Income is smaller than the limit")
else:
    print("Equal")
"""

# mini app

"""
limit = 50000 
store_name = input("Enter the store name:")
income = int(input("Enter the income:"))

if(income > limit):
    print(store_name + " Income is bigger than the limit")
elif(income < limit):
    print(store_name + " Income is smaller than the limit")
else:
    print(store_name + " Equal")
"""

# for

"""
students = ["mehmet","selim","süleyman","bayezid"]

for i in students:
    print(i)

a = [1,2,3,4,5,6,7,8,9,10]

for i in a:
    print(i)

salaries = [1000,2000,3000,4000,5000]

def new_salary(x):
    print(x * 20/100 + x)

for i in salaries:
    new_salary(i)

print("------------------")
salaries = [1000,2000,3000,4000,5000]

def salary_top(x):
    print(x * 10/100 + x)

def salary_sub(x):
    print(x * 20/100 + x)

for i in salaries:
    if(i >= 3000):
        salary_top(i)
    else:
        salary_sub(i)
"""

# break & continue

"""
salaries = [1000,2000,3000,4000,5000]

for i in salaries:
    if i == 3000:
        break
    print(i)

print("------------")

for i in salaries:
    if i == 3000:
        continue
    print(i)
"""

# while 

"""
num = 1

while num < 11:
    print(num)
    num += 1
"""
# class

"""
class data_scientist:
    print("hello world")
"""

# class attributes

"""
class data_scientist():
    department = ''
    sql = "Yes"
    years_of_experience = 0
    knows_languages = []

print(data_scientist.department)
print(data_scientist.sql)

data_scientist.sql = "No"
print(data_scientist.sql)
print("-------------------")

ali = data_scientist()
print(ali.sql)
print(ali.department)
ali.knows_languages.append("Python")
print(ali.knows_languages)
print("-------------------")

veli = data_scientist()
print(veli.sql)
print(veli.knows_languages)
print("-------------------")

class DataScientist():
    knows_languages = ["R","PYTHON"]
    department = ''
    sql = ''
    years_of_experience = 0
    def __init__(self):
        self.knows_languages = []
        self.department = ''

ali = DataScientist()
print(ali.knows_languages)
veli = DataScientist()
print(veli.knows_languages)

ali.knows_languages.append("PYTHON")
print(ali.knows_languages)
print(veli.knows_languages)
veli.knows_languages.append("R")
print(veli.knows_languages)
print(DataScientist.knows_languages)
print("-------------------")

print(DataScientist.department)
ali.department = "software engineering"
print(DataScientist.department)
print(veli.department)
print(ali.department)
veli.department = "game developer"
print(veli.department)
print(DataScientist.department)
"""

# Instance Methods

"""
class DataScientist():
    employees = []
    def __init__(self):
        self.knows_languages = []
        self.department = ''
    def add_language(self, new_language):
        self.knows_languages.append(new_language)

ali = DataScientist()
print(ali.knows_languages)
print(ali.department)
print("-------------------")

veli = DataScientist()
print(veli.knows_languages)
print(veli.department)
print("-------------------")

print(dir(DataScientist))

ali.add_language("Python")
print(ali.knows_languages)

veli.add_language("R")
print(veli.knows_languages)
"""

# inheritance

"""
class Employees():
    def __init__(self):
        self.FirstName = ""
        self.LastName = ""
        self.Address = ""

class DataScience(Employees):
    def __init__(self):
        self.Programming = ""

class Marketing(Employees):
    def __init__(self):
        self.StoryTelling = ""

class New_Employee():
    def __init__(self, FirstName, LastName, Address):
        self.FirstName = FirstName
        self.LastName = LastName
        self.Address = Address

ali = New_Employee("a","b","c")
print(ali.FirstName)
"""

# Pure functions

"""
A = 9

def impure_sum(b):
    return b + A

def pure_sum(a,b):
    return a + b

print(impure_sum(4))
print(pure_sum(3,4))
"""

# Anonymous functions

"""
def old_sum(a,b):
    return a + b
print(old_sum(4,5))
print("---------------")

new_sum = lambda a,b: a + b
print(new_sum(4,5))

l = [("b",3),("a",8),("d",12),("c",1),]
print(sorted(l, key = lambda x: x[1]))
"""

# Vectorel Operations
#OOP

"""
a = [1,2,3,4]
b = [2,3,4,5]

ab = []

for i in range(0, len(a)):
    ab.append(a[i]*b[i])

print(ab)
"""

#FP

"""
import numpy as np

a = np.array([1,2,3,4])
b = np.array([2,3,4,5])
print(a*b)
"""

# map & filter & reduce

"""
l1 = [1,2,3,4,5]

for i in l1:
    print(i + 10)

print(list(map(lambda x: x + 10, l1)))

l2 = [1,2,3,4,5,6,7,8,9,10]
print(list(filter(lambda x: x % 2 == 0, l2)))

from functools import reduce

l3 = [1,2,3,4]
print(reduce(lambda a,b: a + b, l3))
"""

# module 
# CalculationModule.py

"""
def new_salary(x):
    print(x * 20/100 + x)

salaries = [1000,2000,3000,4000,5000]

# test.py

import CalculationModule 
CalculationModule.new_salary(1000)

import CalculationModule as cm
cm.new_salary(2000)

from CalculationModule import new_salary
new_salary(4000)

import CalculationModule as cm
print(cm.salaries)
"""

# exceptions

a = 10
b = 0

try:
    print(a/b)
except ZeroDivisionError:
    print("ZeroDivisionError")

a = 10
b = "2"

try:
    print(a/b)
except TypeError:
    print("Type Error")


a = 10
b = 2

try:
    print(a/b)
except TypeError:
    print("Type Error")