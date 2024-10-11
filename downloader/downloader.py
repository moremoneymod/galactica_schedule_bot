import urllib.request
import requests
from bs4 import BeautifulSoup

url = 'https://galaxycollege.ru/students/schedule/'
r = requests.get(url)

soup = BeautifulSoup(r.text, 'html.parser')
link = soup.find(name="a", attrs={"class": "mr-1 sf-link sf-link-theme sf-link-dashed"})

file_link = "https://galaxycollege.ru" + link["href"]

file = requests.get(file_link)

with open("shedule.xls", 'wb') as f:
    f.write(file.content)