__author__ = 'Jan Okruta'
__copyright__ = 'Copyright 2018, Amazon Price Alert Crawler'

__license__ = 'GPL'
__version__ = '0.9.0'
__maintainer__ = 'Jan Okruta'
__email__ = 'jan.okruta@gmail.com'

import smtplib
from datetime import datetime

import requests
from bs4 import BeautifulSoup

EMAIL_USER = 'email@abc.com'
EMAIL_PASS = '123'
EMAIL_HOST = 'smtp.mailgun.org'


def send_mail(subject, content):
    username = EMAIL_USER
    password = EMAIL_PASS
    sender = f'Amazon Price Alert Crawler <{EMAIL_USER}>'
    to = 'Janek <jan.okruta@gmail.com>'

    for ill in ['\n', '\r']:
        subject = subject.replace(ill, ' ')

    headers = {
        'Content-Type': 'text/html; charset=utf-8',
        'Content-Disposition': 'inline',
        'Content-Transfer-Encoding': '8bit',
        'From': sender,
        'To': to,
        'Date': datetime.now().strftime('%a, %d %b %Y  %H:%M:%S %Z'),
        'X-Mailer': 'python',
        'Subject': subject
    }

    # create the message
    msg = ''
    for key, value in headers.items():
        msg += '%s: %s\n' % (key, value)

    # add contents
    msg += '\n%s\n' % content

    server = smtplib.SMTP('smtp.eu.mailgun.org', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(headers['From'], headers['To'], msg.encode('utf8'))
    server.quit()


def book_prices(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, 'lxml')
    price_spans = soup.find_all('span', {'class': ['a-offscreen']})
    return [float(span.contents[0].replace('$', '')) for span in price_spans]


if __name__ == '__main__':
    # your amazon.com public wish list link
    WISH_LIST_URL = 'https://www.amazon.com/hz/wishlist/ls/3O2IVT8V1D1A9?type=wishlist&filter=unpurchased&sort=price-asc'
    PREFERRED_PRICE = 10

    books_to_buy = 0
    print('Book prices:')
    print(book_prices(WISH_LIST_URL))
    for price in book_prices(WISH_LIST_URL):
        if price <= PREFERRED_PRICE:
            books_to_buy += 1

    if books_to_buy > 0:
        s = 's' if books_to_buy > 1 else ''
        sub = f'You can buy {books_to_buy} book{s} below ${PREFERRED_PRICE} from your Amazon Wish List'
        message = f'<h1><a href="{WISH_LIST_URL}">Check out your wished book{s}</a></h1>'
        send_mail(sub, message)
