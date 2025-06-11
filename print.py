from random import randint

print("Hello world?")

number = randint(1,100)

if (number == 11):
    raise ValueError("Out of range error")

print("Run successful")

