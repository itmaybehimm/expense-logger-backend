import hashlib
import datetime


def customSHA256(string):
    if type(string) != str:
        string = str(string)
    h = hashlib.new("SHA256")
    h.update(string.encode())
    return h.hexdigest()


def strtodate(str):
    date_obj = datetime.datetime.strptime(str, '%m-%d-%Y').date()
    return date_obj
