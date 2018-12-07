import requests 
from bs4 import BeautifulSoup

FormData={
    'search':'apple',
    'commit':'search',
    'authenticity_token':'QrlBkUY0PIGkfC/QXemwtqMK8+QNMcC4/j2iPR2xE5s='
}
with requests.Session() as s: 
    res = s.post("https://www.myfitnesspal.com/food/search",data=FormData)
    soup = BeautifulSoup(res.text, 'lxml')
    print (soup.find_all(class_="brand"))

    