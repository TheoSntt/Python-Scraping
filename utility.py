import requests
from bs4 import BeautifulSoup
from word2number import w2n


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


def format_info(soup, url):
    info_string = ""
    # The URL is already known, it doesn't need to be scraped from the page
    info_string += url + ','

    # The title can be recovered through the h1 section
    info_string += '"' + soup.find('h1').text.replace('"', """""") + '",'

    # For the description, the div is not named and doesn't have class. So we access it by finding the previous div
    # and then using the function findNext of BeautifulSoup
    if soup.find(id="product_description") is not None:
        info_string += '"'\
            + soup.find(id="product_description").findNext('p').text.replace(' ...more', '').replace('"', """""") + '",'
    else:
        info_string += '"No description",'

    # The UPC, prices, and number available are stored in a table through which we can iterate
    tds = soup.findAll('td')
    info_string += tds[0].text + ','
    # For both prices value, removing the pound sign and converting to float
    price_inc = tds[3].text[1:]
    info_string += '"' + price_inc.replace(".", ",") + '",'
    price_excl = tds[3].text[1:]
    info_string += '"' + price_excl.replace(".", ",") + '",'
    # Replace statements to remove unwanted information
    info_string += tds[5].text.replace("In stock (", "").replace(" available)", "") + ','

    # The category is only visible in a link on top of the page. We can access it by finding all 'li' elements
    liz = soup.findAll('li')
    # Some blank spaces and \n where present. Removed them with the strip method.
    info_string += liz[2].text.strip() + ','

    # The review rating is found in the name of the div containing the stars
    # Getting the div
    rating_div = soup.select("p[class^=star-rating]")[0]
    # Getting the number written in all letters
    rating_text = rating_div["class"][1]
    # Converting it to number
    rating_nb = w2n.word_to_num(rating_text)
    info_string += str(rating_nb) + ','

    # There is only one image in the page, so we can acess the link of the image by searching
    # the one img div with bs4
    raw_link = soup.find('img')['src']
    final_link = "http://books.toscrape.com/" + raw_link[6:]
    info_string += final_link + '\n'

    # Retrieving the book name from the URL to name the saved image
    img_name = url.split("/")[-2].split('_')[0]

    # Returning our final object
    print(info_string)
    return info_string, final_link, img_name


def get_books_url_from_category_page(page, url_list):
    raw_url_list = page.find('ol', {'class': 'row'}).findChildren("h3")
    # Iterating through each URL of this page
    for raw_url in raw_url_list:
        # print(raw_url.findChildren("a")[0]['href'])
        book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        url_list.append(book_url)

