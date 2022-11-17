import requests
from bs4 import BeautifulSoup

url = 'http://example.com/'

response = requests.get(url)

if response.ok:
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find('title')
    print(title.text)
else:
    print("La requête a échoué")