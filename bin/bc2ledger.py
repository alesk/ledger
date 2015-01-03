#!/usr/bin/env python
"""
Converting export from klik to ledgger format
"""

import csv
import re
from string import strip
from sys import argv
from datetime import datetime
from os.path import basename

# Predefined transactions
patterns = [
    (re.compile(".*bankomat dvig", re.I), [("From", "Assets:Bank:Checking"), ("To", "Assets:Cache")]),
    (re.compile(".*nadomestilo za dvig", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Bank:Withdraw Provision")]),
    (re.compile(".*uporabnina nlb klik", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Bank:Operation")]),
    (re.compile(".*petrol", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Auto:Gas")]),
    (re.compile(".*interspar", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Groceries")]),
    (re.compile(".*hervis", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Clothing")]),
    (re.compile(".*intersport", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Clothing")]),
    (re.compile(".*provizija", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Bank:Provision")]),
    (re.compile(".*tk storitev", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Utils:Tv")]),
    (re.compile(".*redne obveznosti", re.I), [("From", "Assets:Bank:Checking"), ("To", "Expenses:Apartment:Common")]),
    (re.compile(".*rtv", re.I), [("From", "RtvSlo:Payable"), ("To", "Expenses:Utils:Tv")]),

    (re.compile(".*skupaj dodatki", re.I), [("From", "Celtra:Income:Sallary"), ("To", "Assets:Bank:Checking")]),
    (re.compile(".*placa", re.I), [("From", "Celtra:Income:Sallary"), ("To", "Assets:Bank:Checking")]),
    (re.compile(".*bonus", re.I), [("From", "Celtra:Income:Bonus"), ("To", "Assets:Bank:Checking")])
    
]

tpl = '''
%(Datum valute)s * %(Opis)s
    ; Source: %(Statement)
    %(To)s  %(Znesek)s
    %(From)s'''

def amount(text):
    return "{:20.2f} EUR".format(float(text.replace('.','').replace(',','.')))
    
def datum(text):
    return datetime.strptime(text, "%d.%m.%Y").strftime("%Y-%m-%d")
    
def transform(dct):
    v_dobro = amount(dct['V dobro'])
    v_breme = amount(dct['V breme'])
    is_v_dobro = True if strip(v_breme) == "0.00 EUR" else False
    return dict([
        ('Datum valute', datum(dct['Datum valute'])),
        ('Znesek', v_dobro if is_v_dobro else v_breme),
        ('Je v dobro', is_v_dobro),
        ('Opis', dct["Opis"]) ])

def add_accounts(t):
    for (p, accounts) in patterns:
        if p.match(t['Opis']):
            return dict(t.items() + accounts)
    if t["Je v dobro"]:
        return dict(t.items() + [("To", "Expenses:XXX"), ("From", "Assets:Bank:Checking")])
    else:
        return dict(t.items() + [("To", "Assets:Bank:Checking"), ("From", "Income::XXX")])


def convert(file_name):
    
    with open(file_name, 'r') as fl:
        r = csv.DictReader(fl, delimiter=";")
        for l in r:
            print tpl % dict(add_accounts(transform(l)).items() + ("Statement", basename(filename)))
            

if __name__ == '__main__':
    input_file = argv[1]
    print "; Conversion of bank statement from '%s'" % basename(input_file)
    convert(input_file)
