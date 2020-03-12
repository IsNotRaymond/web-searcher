import re
import operator
from bson.son import SON
from pymongo import MongoClient
import requests
import requests_cache
from bs4 import BeautifulSoup

# Install cache to improve load performance
requests_cache.install_cache('cache')

# MongoDB Configurations
CLUSTER_LINK = 'https://cloud.mongodb.com/v2/5e5063ee0c3bc54dcb1f60f2'
DATABASE_NAME = 'web-searcher'
COLLECTIONS_NAME = 'urls'
URL_SERVER = 'mongodb+srv://Artur:Clashofclans00@mongo-qiim9.gcp.mongodb.net/test?retryWrites=true&w=majority'

client_mongo = MongoClient(URL_SERVER)
database = client_mongo[DATABASE_NAME]
collections = database[COLLECTIONS_NAME]


def main():
    keyword = input('Keyword: ').lower()
    url = handle_url(input('URL: '))
    depth = handle_input('Profundidade de pesquisa (Tempo de pesquisa aumenta exponencialmente. Recomendado: 2): ')
    set_links = {}
    search(url, keyword, set_links, depth)

    q = collections.find({'words': {'$elemMatch': {'keyword': keyword}}})

    print('\nAchamos que os links abaixo podem ser relevantes: ')
    links = {}

    for query in q:
        links[query['link']] = query['words'][0]['percent']

    sorted_d = sorted(links.items(), key=operator.itemgetter(1), reverse=True)

    show_links(sorted_d)


def show_links(sorted_d):
    i = 0
    if len(sorted_d) >= 15:
        for item in sorted_d:
            if i < 15:

                print('%d: %s' % (i + 1, item[0]))
            else:
                break
            i += 1
    else:
        for item in sorted_d:
            print('%d: %s' % (i + 1, item[0]))
            i += 1


def handle_input(msg):
    while True:
        value = input(msg)

        if value.isnumeric():
            return int(value)

        print('Erro: Digite um número correto')


def handle_url(url):
    if not url.startswith('http'):
        if not url.startswith('www.'):
            return 'https://www.' + url
        return 'https://' + url

    return url


def extract_links(soup):
    urls = []

    for anchor_tag in soup.find_all('a'):
        urls.append(anchor_tag.get('href'))

    return urls


def handle_text(body):
    regex_words = re.compile('[a-zA-ZÀ-ú]+')
    regex_split = re.compile('\s+')

    lines = regex_split.split(body)
    ignore = ['table', 'head', 'div', 'solid', 'body', 'arial', 'repeat', 'all', 'span', 'input', 'header', 'sans',
              'rgba', 'pagecommentsinfoattachments', 'page', 'search']
    words = {}

    for line in lines:
        match = regex_words.match(line)

        if match is not None:
            word = match.group().lower()

            if 30 > len(word) > 2 and word not in ignore:
                if word in words.keys():
                    words[word] += 1
                else:
                    words[word] = 1

    return words


# noinspection PyBroadException
def search(url, keyword, visited, max_depth=3, depth=0):
    if depth < max_depth:
        try:
            soup = BeautifulSoup(requests.get(url, allow_redirects=True).text, 'html.parser')

            # Remove the javascript of the body (most of them I hope)
            for script in soup.find_all('script', src=False):
                script.decompose()

            words = handle_text(soup.get_text())

            print(url)
            print(words)
            total = sum(words.values())
            amount = words[keyword] if keyword in words.keys() else 0
            percent = amount / total * 100 if amount != 0 else 0

            if amount == 0:
                return

            if url not in visited.keys():
                add_database(url, keyword, amount, percent)
                visited[url] = {keyword: {'amount': amount, 'percent': percent}}

            for link in extract_links(soup):
                if link not in visited and link is not None and link.startswith('http'):
                    search(link, keyword, visited, max_depth, depth + 1)
        except:
            pass


def add_database(url, keyword, amount, percent):
    q = collections.find_one({'link': url})

    if q is None:
        collections.insert_one({'link': url,
                                'words': [SON([('keyword', keyword), ('amount', amount), ('percent', percent)])]})
        print('-' * 20)
        print('[DB_LOG] New entry on database: %s' % url)

    else:
        array = q['words']

        for entry in array:
            if entry['keyword'] == keyword:
                print('-' * 20)
                print('[DB_LOG] The same values are in the Database: %s' % url)
                return

        array.append(SON([('keyword', keyword), ('amount', amount), ('percent', percent)]))

        collections.update_one({'link': url}, {'$set': {'words': array}})

        print('-' * 20)
        print('[DB_LOG] Updated entry on database: %s' % url)


if __name__ == '__main__':
    main()
