'''
Contains module to Login in Instagram and return user_id of an instagram
profile
'''

import pickle
from bs4 import BeautifulSoup
import json
import random
import re
import os
import requests


def test_login(session):
    variables = {}
    variables_json = json.dumps(variables,separators=(',',':'))
    host = 'www.instagram.com/graphql/query/'
    data = "d6f4427fbe92d846298cf93df0b937d3"
    params = {
        'query_hash': data,
        'variables': variables_json
    }
    res = session.get('https://{}'.format(host),params=params)
    return res.json()['data']['user'] is not None


def login(username, password):
    BASE_URL = 'https://www.instagram.com/accounts/login/'
    LOGIN_URL = BASE_URL + 'ajax/'
    headers_list = [
        "Mozilla/5.0 (Windows NT 5.1; rv:41.0) Gecko/20100101"
        " Firefox/41.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2)"
        " AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2"
        " Safari/601.3.9",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0)"
        " Gecko/20100101 Firefox/15.0.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36"
        " Edge/12.246"
    ]
    USER_AGENT = headers_list[random.randrange(0, 4)]
    session = requests.Session()
    session.headers = {'user-agent': USER_AGENT}
    session.headers.update({'Referer': BASE_URL})
    req = session.get(BASE_URL)
    soup = BeautifulSoup(req.content, 'html.parser')
    body = soup.find('body')

    pattern = re.compile('window._sharedData')
    script = body.find("script", text=pattern)

    script = script.get_text().replace('window._sharedData = ', '')[:-1]
    data = json.loads(script)

    csrf = data['config'].get('csrf_token')
    login_data = {'username': username, 'password': password}
    session.headers.update({'X-CSRFToken': csrf})
    login = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
    was_successful = test_login(session=session)
    if was_successful:
        if os.path.exists('cookies') and os.path.isdir('cookies'):
            pass
        else:
            os.mkdir('cookies')
        with open('cookies'+'/'+username, 'wb') as f:
            pickle.dump(session.cookies, f)
            return "Login Sucessful"
    else:
        return 'Login Unsucessful! :('

def get_id(username):
    link = "https://www.instagram.com/" + username + "/"
    try:
        page = requests.get(link)
    except requests.exceptions.MissingSchema:
        print('Please Enter a valid url')
    soup2 = BeautifulSoup(page.text, 'lxml')
    scrips = soup2.find_all('script')
    for i in scrips:
        if '"id":' in i.text:
            scrip = scrips[scrips.index(i)].text
    scrip = json.loads(
        '{'+scrip[scrip.index('"id":'):scrip.index(',', scrip.index('"id":'))]+'}')
    return scrip['id']
