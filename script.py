import requests
from utility import send_request, format_info, get_books_url_from_category_page
import math
from pathlib import Path
from datetime import date
import time
import concurrent.futures


def get_info_and_image_for_a_book(url):
    book_page_content = send_request(url)
    output_string, img_url, img_name = format_info(book_page_content, url)
    str_liste.append(output_string)
    # Exporting the image too
    img_data = requests.get(img_url).content
    with open(out_path + img_name + '.jpg', 'wb') as handler:
        handler.write(img_data)


start_time = time.time()
# Sending a request to the homepage of books.toscrape
theUrl = "http://books.toscrape.com/index.html"
soup = send_request(theUrl)
# Retrieving the category list from the HTML of the page, using BeautifulSoup
categories = soup.findAll('ul')[2]
categories_urls = {}
for cat in categories.findChildren('a'):
    cat_url = "http://books.toscrape.com/" + cat['href']
    file_name = cat_url.split("/")[-2].split("_")[0]
    categories_urls[file_name] = cat_url
# At this point, we have a dict of categories URLs. For each category, we need all the books URLs.
# We are going to loop through that object. So the following executes for each category
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
    get_books_url_from_category_page(category_content, book_urls)
    # This loop is entered only if there are more than 20 books in the category.
    if nb_pages > 1:
        for nb in range(2, nb_pages + 1):
            # For each other page of result, builds and query the URL, and extract the books URL
            nxt_page_url = category_url[:-10] + "page-" + str(nb) + ".html"
            page_content = send_request(nxt_page_url)
            get_books_url_from_category_page(page_content, book_urls)
    # At this point, we have, for a given category, a complete list of book URLs
    # We are now going to query each URL, extract the needed information from each page, and write it to CSV file.
    # Building the file path for outputing the files
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    out_path = 'results/' + d1 + "/" + file_name + "/"
    Path(out_path).mkdir(parents=True, exist_ok=True)
    # Sending the parallel requests to get all the info
    str_liste = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_info_and_image_for_a_book, book_urls)
    # Writing the CSV file
    with open(out_path + file_name + '.csv', 'w', encoding='utf-8') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, " \
                     "price_excluding_tax, number_available, category, review_rating, image_url\n "
        file.write(header_str)
        for str_line in str_liste:
            file.write(str_line)
        # For each book. Going to query, extract the data, and write it to the file
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_info_and_image_for_a_book, book_urls)
        """
        """
        for book_url in book_urls:
            # Sending request to the URL and writing the info to the CSV
            get_info_and_image_for_a_book(book_url)

            book_page_content = send_request(book_url)
            output_string, img_url, img_name = format_info(book_page_content, book_url)
            file.write(output_string)
            # Exporting the image too
            img_data = requests.get(img_url).content
            with open(out_path + img_name + '.jpg', 'wb') as handler:
                handler.write(img_data)"""

print("time elapsed: {:.2f}s".format(time.time() - start_time))




