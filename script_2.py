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
        print(response)


def get_books_url(soup, file_name):
    # print(soup)
    books_urls = []
    nb_pages = math.ceil(int(soup.find('form').findChildren()[1].text)/20)
    print("Number of pages for this category : " + str(nb_pages))
    # Extract books URL of the first pages of result anyway
    extract_books_urls(soup,file_name)
    # If there are more than one page, get the books URL from the other pages
    if nb_pages > 1:
        for nb in range(2, nb_pages + 1):
            nxt_page_url = theURL[:-10] + "page-" + str(nb) + ".html"
            extract_books_urls(send_request(nxt_page_url), file_name)


def write_a_book_in_csv(book_url, file_name):
    with open('results/' + file_name + '.csv', 'w', encoding='utf-8') as file:
        file.write(format_info(send_request(book_url), book_url))


def extract_books_urls(soup, file_name):
    raw_url_list = soup.find('ol', {'class': 'row'}).findChildren("h3")
    for raw_url in raw_url_list:
        url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        write_a_book_in_csv(format_info(send_request(url), url), file_name)
        # print(url)


def write_file(list_url):
    with open('results/test.csv', 'w', encoding='utf-8') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, price_excluding_tax, number_available, category, review_rating, image_url\n"
        file.write(header_str)
        for i in list_url:
            file.write(format_info(send_request(i), i))
            # print(i)


url_list = []
"""
content, nb_page = determine_number_of_page(send_request(theURL))
get_books_url(content)
write_file(url_list)
"""


