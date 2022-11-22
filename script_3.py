import requests
from bs4 import BeautifulSoup
from script_2 import send_request
from script import format_info
import math
from pathlib import Path


theUrl = "http://books.toscrape.com/index.html"
soup = send_request(theUrl)


categories = soup.findAll('ul')[2]
# writing the header of the csv file
"""
# For each category, get the URL and recover all the books URL
for cat in categories.findChildren('a'):
    cat_url = "http://books.toscrape.com/" + cat['href']
    print(cat_url)
    file_name = cat_url.split("/")[-2]
    # Creating the CSV file for each category
    with open('results/' + file_name + '.csv', 'w', encoding='utf-8') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, " \
                     "price_excluding_tax, number_available, category, review_rating, image_url\n "
        file.write(header_str)
        # Sending a first request to the category URL, to determine if there are multiple pages, and get the books URL
        cat_content = send_request(cat_url)
        nb_pages = math.ceil(int(cat_content.find('form').findChildren()[1].text) / 20)
        print("Number of pages for category " + file_name + " : " + str(nb_pages))
        # Extract books URL of the first pages of result anyway
        # So function that get the URLs for one page
        raw_url_list = cat_content.find('ol', {'class': 'row'}).findChildren("h3")
        # Iterating through each URL of this page
        for raw_url in raw_url_list:
            print(raw_url.findChildren("a")[0]['href'])
            book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
            print(book_url)
            # Sending request to the URL and writing the info to the CSV
            file.write(format_info(send_request(book_url), book_url))
        # If there are more than one page, get the books URL from the other pages
        if nb_pages > 1:
            for nb in range(2, nb_pages + 1):
                nxt_page_url = cat_url[:-10] + "page-" + str(nb) + ".html"
                soup = send_request(nxt_page_url)
                # So function that get the URLs for one page
                raw_url_list = soup.find('ol', {'class': 'row'}).findChildren("h3")
                # Iterating through each URL of this page
                for raw_url in raw_url_list:
                    book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
                    # Sending request to the URL and writing the info to the CSV
                    file.write(format_info(send_request(book_url), book_url))
"""

categories_urls = {}
for cat in categories.findChildren('a'):
    cat_url = "http://books.toscrape.com/" + cat['href']
    file_name = cat_url.split("/")[-2].split("_")[0]
    categories_urls[file_name] = cat_url
    # TODO : Maybe put the header righting in the next loops as writing will be done there too
    """
    with open('results/' + file_name + '.csv', 'w', encoding='utf-8') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, " \
                     "price_excluding_tax, number_available, category, review_rating, image_url\n "
        file.write(header_str)"""

# print(categories_urls)
# So now we have a dict of categories URLs. For each category, we need all the books URL.
for key in categories_urls:
    # For each category of book, declare the file name, the category URL, the book urls list
    file_name = key
    category_url = categories_urls[key]
    book_urls = []
    # Get the HTML of the category page
    category_content = send_request(category_url)
    # Determine the number of pages of result
    nb_pages = math.ceil(int(category_content.find('form').findChildren()[1].text) / 20)
    print("Number of pages for category " + file_name + " : " + str(nb_pages))
    # Extract books URL of the first pages of result
    raw_url_list = category_content.find('ol', {'class': 'row'}).findChildren("h3")
    # Iterating through each URL of this page
    for raw_url in raw_url_list:
        # print(raw_url.findChildren("a")[0]['href'])
        book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        book_urls.append(book_url)
    # This loop is entered only if there are more than 20 books in the category.
    # Retrieves the books url of the other pages of results
    if nb_pages > 1:
        for nb in range(2, nb_pages + 1):
            nxt_page_url = category_url[:-10] + "page-" + str(nb) + ".html"
            page_content = send_request(nxt_page_url)
            raw_url_list = page_content.find('ol', {'class': 'row'}).findChildren("h3")
            # Iterating through each URL of this page
            for raw_url in raw_url_list:
                book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
                book_urls.append(book_url)
    # print(book_urls)
    # At this point, we have, for each category, a complete list of book URLs
    # We are now going to query each URL, extract the needed information from each page, and write it to CSV file.
    Path('results/' + file_name).mkdir(parents=True, exist_ok=True)
    with open('results/' + file_name + '/' + file_name + '.csv', 'w', encoding='utf-8') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, " \
                     "price_excluding_tax, number_available, category, review_rating, image_url\n "
        file.write(header_str)
        for book_url in book_urls:
            # Sending request to the URL and writing the info to the CSV
            book_page_content = send_request(book_url)
            output_string, img_url, img_name = format_info(book_page_content, book_url)
            file.write(output_string)
            img_data = requests.get(img_url).content
            with open('results/' + file_name + '/' + img_name + '.jpg', 'wb') as handler:
                handler.write(img_data)





