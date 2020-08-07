import os
import math
import requests
from bs4 import BeautifulSoup


def analyse_search(as_search_category):
    as_page_limit, as_page_data = '', ''
    as_skip_term = False
    search_url = 'https://jisho.org/search/' + as_search_category
    page = requests.get(search_url)
    page_soup = BeautifulSoup(page.content, 'html.parser')
    if not page_soup.find(class_='result_count'):
        print('No usable results found.')
        as_skip_term = True
    else:
        as_page_info = page_soup.find(class_='result_count').text
        as_page_limit = math.ceil(int(as_page_info.replace(' — ', '').replace(' found', '')) / 20)
        if as_page_limit > 2000:
            as_page_limit = 2000
            print('Hit page limit.')
            as_skip_term = True
        as_page_data = page_soup.find_all(class_='character literal japanese_gothic')
    return as_page_limit, as_page_data, as_skip_term


def retrieve_results(rr_search_category, rr_page_count):
    search_url = 'https://jisho.org/search/' + rr_search_category + '?page=' + str(rr_page_count)
    page_soup = BeautifulSoup(requests.get(search_url).content, 'html.parser')
    rr_page_data = page_soup.find_all(class_='character literal japanese_gothic')
    print('Fetching ' + str(len(rr_page_data)) + ' results from page ' + str(rr_page_count) + '.')
    return rr_page_data


def save_kanji():
    with open('data/kanji_data/' + filename + '/' + filename + '_kanji_list.txt', 'a') as list_file:
        list_file.write(str(entry.text).replace('\n', '').replace('\r', '').replace(' ', ''))
        list_file.write('\n')


kanji_category_list = [line.rstrip('\n') for line in open('data/kanji_category_list.txt')]
for search_term in kanji_category_list:
    print("\nSearching Jisho.org for: '" + search_term + "'.")
    search_data, page_count = [], 1
    page_limit, page_data, skip_term = analyse_search(search_term)
    if skip_term:
        continue
    print(str(page_limit) + ' pages found.\n')
    print('\nFetching ' + str(len(page_data)) + ' results from page ' + str(page_count) + '.')
    filename = search_term.replace('%23kanji %23', '').replace(':', '%3A')
    if not os.path.exists('data/kanji_data/' + filename):
        os.makedirs('data/kanji_data/' + filename)
    for entry in page_data:
        save_kanji()
    while page_count < page_limit:
        page_count += 1
        page_data = retrieve_results(search_term, page_count)
        for entry in page_data:
            save_kanji()
