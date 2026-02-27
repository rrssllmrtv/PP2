#1
def square(n):
    for i in range(1, n + 1):
        yield i * i

for x in square(5):
    print(x)

#2
def even(n):
    for i in range(n + 1):
        if i % 2 == 0:
            yield i

n = int(input())
result = []

for x in even(n):
    result.append(str(x))

print(", ".join(result))

#3
def div(n):
    for i in range(n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())

for x in div(n):
    print(x)

#4
def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

for x in squares(3, 7):
    print(x)

#5
def all_nums(n):
    while n >= 0:
        yield n
        n -= 1

for x in all_nums(5):
    print(x)