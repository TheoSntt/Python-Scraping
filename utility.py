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
    try:
        info_string += '"' + soup.find('h1').text.replace('"', """""") + '",'
    except:
        info_string += '"",'

    # For the description, the div is not named and doesn't have class. So we access it by finding the previous div
    # and then using the function findNext of BeautifulSoup
    try:
        info_string += '"'\
            + soup.find(id="product_description").findNext('p').text.replace(' ...more', '').replace('"', """""") + '",'
    except:
        info_string += '"",'

    # The UPC, prices, and number available are stored in a table through which we can iterate
    tds = soup.findAll('td')
    try:
        info_string += tds[0].text + ','
    except:
        info_string += '"",'
    # For both prices value, removing the pound sign and converting to float
    try:
        price_inc = tds[3].text[1:]
        info_string += '"' + price_inc.replace(".", ",") + '",'
    except:
        info_string += '"",'
    try:
        price_excl = tds[3].text[1:]
        info_string += '"' + price_excl.replace(".", ",") + '",'
    except:
        info_string += '"",'
    # Replace statements to remove unwanted information
    try:
        info_string += tds[5].text.replace("In stock (", "").replace(" available)", "") + ','
    except:
        info_string += '"",'

    # The category is only visible in a link on top of the page. We can access it by finding all 'li' elements
    liz = soup.findAll('li')
    # Some blank spaces and \n where present. Removed them with the strip method.
    try:
        info_string += liz[2].text.strip() + ','
    except:
        info_string += '"",'

    # The review rating is found in the name of the div containing the stars
    try:
        # Getting the div
        rating_div = soup.select("p[class^=star-rating]")[0]
        # Getting the number written in all letters
        rating_text = rating_div["class"][1]
        # Converting it to number
        rating_nb = w2n.word_to_num(rating_text)
        info_string += str(rating_nb) + ','
    except:
        info_string += '"",'

    # There is only one image in the page, so we can acess the link of the image by searching
    # the one img div with bs4
    try:
        raw_link = soup.find('img')['src']
        final_link = "http://books.toscrape.com/" + raw_link[6:]
        info_string += final_link + '\n'
    except:
        info_string += '"",'

    # Retrieving the book name from the URL to name the saved image
    img_name = url.split("/")[-2].split('_')[0]

    # Returning our final object
    print(info_string)
    return info_string, final_link, img_name


def format_info_for_csv_lib(soup, url):
    info_list = []
    # The URL is already known, it doesn't need to be scraped from the page
    info_list.append(url)
    if 'fire' in url:
        print(url)

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
    # For both prices value, removing the pound sign and converting to float
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
    # Replace statements to remove unwanted information
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
    # print(info_list)
    return info_list, final_link, img_name


def get_books_url_from_category_page(page, url_list):
    raw_url_list = page.find('ol', {'class': 'row'}).findChildren("h3")
    # Iterating through each URL of this page
    for raw_url in raw_url_list:
        # print(raw_url.findChildren("a")[0]['href'])
        book_url = "http://books.toscrape.com/catalogue" + raw_url.findChildren("a")[0]['href'][8:]
        url_list.append(book_url)