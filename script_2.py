import requests
from bs4 import BeautifulSoup
import math
from script import format_info

# This script aims to retrieve all the book URL of a given category
theURL = "http://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"


def send_request(url):
    response = requests.get(url)
    if response.ok:
        # Converting the response to UTF8 encoding
        # Added this step to troubleshoot the issue with non ASCII characters such as the english pound symbol
        if response.encoding != 'utf-8':
            response.encoding = 'utf-8'
        # Creating a BeautifulSoup object to easily parse through the response
        soup = BeautifulSoup(response.text, "html.parser")
        return soup
    else:
        print("La requête a échoué")


def determine_number_of_page(soup):
    # print(soup)
    nb_pages = math.ceil(int(soup.find('form').findChildren()[1].text)/20)
    print("Number of pages for this category : " + str(nb_pages))
    return soup, nb_pages


def extract_urls(soup):
    raw_url_list = soup.find('ol', {'class': 'row'}).findChildren("h3")
    for raw_url in raw_url_list:
        url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        # print(url)
        url_list.append(url)


def get_books_url(soup):
    extract_urls(soup)
    if nb_page > 1:
        for nb in range(2, nb_page+1):
            nxt_page_url = theURL[:-10] + "page-"+ str(nb) + ".html"
            extract_urls(send_request(nxt_page_url))
        return url_list


url_list = []
content, nb_page = determine_number_of_page(send_request(theURL))
get_books_url(content)

with open('results/test.csv', 'w', encoding='utf-8') as file:
    # Writing the header
    header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, price_excluding_tax, number_available, category, review_rating, image_url\n"
    file.write(header_str)
    for i in url_list:
        file.write(format_info(send_request(i), i))
        # print(i)
