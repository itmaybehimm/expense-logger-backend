import hashlib
import datetime
import math
import random


def is_special_char(ch):
    special_char = ['!', '@', '#', '$', '%', '^', '&', '*', '_', '-']
    if (ch in special_char):
        return True
    return False


def password_valid(password):
    l, u, p, d = 0, 0, 0, 0
    s = password
    if (len(s) >= 8):
        for i in s:

            # counting lowercase alphabets
            if (i.islower()):
                l += 1

            # counting uppercase alphabets
            if (i.isupper()):
                u += 1

            # counting digits
            if (i.isdigit()):
                d += 1

            # counting the mentioned special characters
            if (is_special_char(i)):
                p += 1
    if (l >= 1 and u >= 1 and p >= 1 and d >= 1 and l+p+u+d == len(s)):
        return True
    else:
        return False


def username_valid(username):
    if (username[0].isdigit() or len(username) < 8 or username[0] == "_"):
        return False
    for i in username:
        if (not i.isdigit() and not i.islower() and not i == '_'):
            return False
    return True


def customSHA256(string):
    if type(string) != str:
        string = str(string)
    h = hashlib.new("SHA256")
    h.update(string.encode())
    return h.hexdigest()


def strtodate(str):
    date_obj = datetime.datetime.strptime(str, '%m-%d-%Y').date()
    return date_obj


# function to generate OTP
def generateOTP():

    # Declare a digits variable
    # which stores all digits
    digits = "0123456789"
    OTP = ""

   # length of password can be changed
   # by changing value in range
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]

    return OTP
