import requests
import bs4
import json
import re
from flask import Flask
from bs4 import BeautifulSoup


if __name__ == '__main__':
    r = requests.get('https://www.toysrus.ca/en/Barbie-3-in-1-DreamCamper-Vehicle-with-Pool%2C-Truck%2C-Boat-and-50-Accessories/E678E3E6.html')
    soup = BeautifulSoup(r.text, 'lxml')
    tag_upc = soup.find(lambda tag : tag.name=='li' and 'UPC' in tag.text)
    print(tag_upc.find('strong').string)