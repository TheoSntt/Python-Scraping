import requests
from bs4 import BeautifulSoup
from word2number import w2n

# This script aims to send a request to a given book URL from bookstoscrape and to scrape the needed information

# First define the URL
theUrl = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'


# Function that sends the requests to the URL
def send_request(url):
    response = requests.get(url)
    if response.ok:
        # Converting the response to UTF8 encoding
        # Added this step to troubleshoot the issue with non ASCII characters such as the english pound symbol
        if response.encoding != 'utf-8':
            response.encoding = 'utf-8'
        # Creating a BeautifulSoup object to easily parse through the response
        soup = BeautifulSoup(response.text, "html.parser")
        # Calling the function that will retrieve the needed information from the result
        scrape_response(soup, url)
    else:
        print("La requête a échoué")


def scrape_response(soup, url):
    # Writing the CSV file header
    with open('test.csv', 'w') as file:
        # Writing the header
        header_str = "product_page_url, title, product_description, universal_product_code, price_including_tax, price_excluding_tax, number_available, category, review_rating, image_url\n"
        file.write(header_str)
        # Writing the infos
        file.write((format_info(soup, url)))


def format_info(soup, url):
    info_string = ""
    # The URL is already known, it doesn't need to be scraped from the page
    info_string += '"' + url + '",'

    # The title can be recovered through the h1 section
    info_string += '"' + soup.find('h1').text + '",'

    # For the description, the div is not named and doesn't have class. So we access it by finding the previous div
    # and then using the function findNext of BeautifulSoup
    info_string += '"' + soup.find(id="product_description").findNext('p').text + '",'

    # The UPC, prices, and number available are stored in a table through which we can iterate
    tds = soup.findAll('td')
    info_string += '"' + tds[0].text + '",'
    # For both prices value, removing the pound sign and converting to float
    price_inc = tds[3].text[1:]
    info_string += '"' + price_inc.replace(".", ",") + '",'
    price_excl = tds[3].text[1:]
    info_string += '"' + price_excl.replace(".", ",") + '",'
    # Replace statements to remove unwanted information
    info_string += '"' + tds[5].text.replace("In stock (", "").replace(" available)", "") + '",'

    # The category is only visible in a link on top of the page. We can access it by finding all 'li' elements
    liz = soup.findAll('li')
    # Some blank spaces and \n where present. Removed them with the strip method.
    info_string += '"' + liz[2].text.strip() + '",'

    # The review rating is found in the name of the div containing the stars
    # Getting the div
    rating_div = soup.select("p[class^=star-rating]")[0]
    # Getting the number written in all letters
    rating_text = rating_div["class"][1]
    # Converting it to number
    rating_nb = w2n.word_to_num(rating_text)
    info_string += '"' + str(rating_nb) + '",'

    # There is only one image in the page, so we can acess the link of the image by searching
    # the one img div with bs4
    raw_link = soup.find('img')['src']
    final_link = "http://books.toscrape.com/" + raw_link[6:]
    info_string += '"' + final_link + "\n"

    # Returning our final object
    # print(info_string)
    return info_string


send_request(theUrl)
