from bs4 import BeautifulSoup

import re
import requests

soup = BeautifulSoup(open('sippa-home.htm').read(), 'html.parser')

print soup.h2.text.split('-')[1].strip()


START_URL = 'http://www.quixada.ufc.br/docente/'

blog_request = requests.get(START_URL)
soup = BeautifulSoup(blog_request.content, 'html.parser')

for div in soup.find_all('div', class_='col-md-10'):
    name = div.h2.text
    position = div.p.text
    url = div.a['href']

    teacher_request = requests.get(url)
    soup_teacher = BeautifulSoup(teacher_request.content, 'html.parser')

    if soup_teacher.em is not None:
        emails = soup_teacher.em.text
    elif len(div.find_all('li')) > 0:
        emails = div.find_all('li')[1].text
    else:
        emails = ''

    print [x.replace(u'\xa0', u'').strip() for x in emails.split(' ') if '@' in x]
