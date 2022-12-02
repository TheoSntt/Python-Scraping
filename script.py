import requests
from bs4 import BeautifulSoup
from word2number import w2n
import math
from pathlib import Path
from datetime import date
import time
import concurrent.futures
import csv


def send_request(url):
    """Base function that send a request to the URL given in argument.
    Create and return a soup object with the query result, so it can be readily used.
    """
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


def get_books_url_from_category_page(page, url_list):
    """Function called of each page of results of a category.
    It extracts the books URL displayed in the page and add them to a list
    """
    raw_url_list = page.find('ol', {'class': 'row'}).findChildren("h3")
    # Iterating through each URL of this page
    for raw_url in raw_url_list:
        book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        url_list.append(book_url)


def format_book_info_for_csv(soup, url):
    """Main HTML parsing function, called on each book page to extract the needed information.
    For each info, navigate to the right HTML tag(s) to get it.
    Return the info in list form so it can be used by the CSV package's function 'write'
    """
    # Instanciate list object to be returned.
    info_list = [url]  # The URL is already known

    # The title can be recovered through the h1 section
    try:
        info_list.append(soup.find('h1').text)
    except:
        info_list.append("")

    # For the description, the div is not named and doesn't have class. So we access it by finding the previous div
    # and then using the function findNext of BeautifulSoup
    try:
        info_list.append(soup.find(id="product_description").findNext('p').text.replace(' ...more', ''))
    except:
        info_list.append("")

    # The UPC, prices, and number available are stored in a table through which we can iterate
    tds = soup.findAll('td')
    try:
        info_list.append(tds[0].text)
    except:
        info_list.append("")
    # For both prices value, removing the pound sign and replacing . with , for better reading in Excel
    try:
        price_inc = tds[3].text[1:]
        info_list.append(price_inc.replace(".", ","))
    except:
        info_list.append("")
    try:
        price_excl = tds[3].text[1:]
        info_list.append(price_excl.replace(".", ","))
    except:
        info_list.append("")

    # Number in stock is written inside a string with unneeded information. Getting rid of it with replace function.
    try:
        info_list.append(tds[5].text.replace("In stock (", "").replace(" available)", ""))
    except:
        info_list.append("")

    # The category is only visible in a link on top of the page. We can access it by finding all 'li' elements
    liz = soup.findAll('li')
    # Some blank spaces and \n where present. Removed them with the strip method.
    try:
        info_list.append(liz[2].text.strip())
    except:
        info_list.append("")

    # The review rating is found in the name of the div containing the stars
    try:
        # Getting the div
        rating_div = soup.select("p[class^=star-rating]")[0]
        # Getting the number written in all letters
        rating_text = rating_div["class"][1]
        # Converting it to number
        rating_nb = w2n.word_to_num(rating_text)
        info_list.append(str(rating_nb))
    except:
        info_list.append("")

    # There is only one image in the page, so we can acess the link of the image by searching
    # the one img div with bs4
    try:
        raw_link = soup.find('img')['src']
        final_link = "http://books.toscrape.com/" + raw_link[6:]
        info_list.append(final_link)
    except:
        info_list.append("")

    # Retrieving the book name from the URL to name the saved image
    img_name = url.split("/")[-2].split('_')[0]

    # Returning our final object
    return info_list, final_link, img_name


def get_info_and_image_for_a_book(url):
    book_page_content = send_request(url)
    output_row, img_url, img_name = format_book_info_for_csv(book_page_content, url)
    row_liste.append(output_row)
    # Exporting the image too
    img_data = requests.get(img_url).content
    with open(img_path + img_name + '.jpg', 'wb') as handler:
        handler.write(img_data)


""" Main part of the script.
Starts by retrieving the category names and URL from the homepage of BooksToScrape.
Then iterates for each category. Retrieves and stores the URLs of all books of that category.
Then send parallel queries to each book URL, to get the needed information and image.
Write all the information in a CSV file.
"""
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
    nb_books_cat = int(category_content.find('form').findChildren()[1].text)
    nb_pages = math.ceil(nb_books_cat / 20)
    print("Extraction des informations et des images des {} livres de la catégorie {}.".format(nb_books_cat, file_name))
    # TODO : Might be worth it to use parallel queries there too, for some categories have up to 150 books. Not sure.
    # Extract books URL of the first pages of result
    get_books_url_from_category_page(category_content, book_urls)
    # This loop is entered only if there are more than 20 books in the category.
    if nb_pages > 1:
        for nb in range(2, nb_pages + 1):
            # For each other page of result, builds and query the URL, and extract the books URL
            nxt_page_url = category_url[:-10] + "page-{}.html".format(nb)
            page_content = send_request(nxt_page_url)
            get_books_url_from_category_page(page_content, book_urls)
    # At this point, we have, for a given category, a complete list of book URLs
    # We are now going to query each URL, extract the needed information from each page, and write it to CSV file.
    # Building the file path for outputing the files
    today = date.today()
    d1 = today.strftime("%Y-%m-%d")
    out_path = 'results/{}/{}/'.format(d1, file_name)
    img_path = out_path + 'images/'
    Path(out_path).mkdir(parents=True, exist_ok=True)
    Path(img_path).mkdir(parents=True, exist_ok=True)
    # Sending the parallel requests to get all the info
    row_liste = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_info_and_image_for_a_book, book_urls)
    # Writing the CSV file
    with open(out_path + file_name + '.csv', 'w', encoding='utf-8', newline='') as csv_file:
        # Creating the csv writer object and writing the header
        writer = csv.writer(csv_file, delimiter=',')
        en_tete = ['product_page_url',
                   'title',
                   'product_description',
                   'universal_product_code',
                   'price_including_tax',
                   'price_excluding_tax',
                   'number_available',
                   'category',
                   'review_rating',
                   'image_url']
        writer.writerow(en_tete)
        for row in row_liste:
            writer.writerow(row)


print("Extraction terminée. Temps d'exécution : {:.2f}s".format(time.time() - start_time))