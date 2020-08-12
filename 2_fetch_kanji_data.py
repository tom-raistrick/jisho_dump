import re
import json
import requests
from bs4 import BeautifulSoup


def kanji_search(ks_entry):
    ks_character, ks_strokes, ks_radical, ks_radical_variants, ks_parts, ks_kanji_variants, ks_meanings, ks_kun, \
        ks_on, ks_grade, ks_jlpt, ks_frequency, ks_comp, ks_kun_comp, ks_on_comp, ks_nanori = \
        '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
    search_url = 'https://jisho.org/search/' + ks_entry + '%20%23kanji'
    page_content = requests.get(search_url).content
    page_soup = BeautifulSoup(page_content, 'html.parser')
    ks_character = page_soup.find(class_='character').text.replace('\n', '')
    ks_strokes = page_soup.find(class_='kanji-details__stroke_count').text \
        .replace('\n', '').replace(' strokes', '').replace(' ', '')
    dictionary_entry_on_yomi = page_soup.find_all(class_='dictionary_entry on_yomi')
    radical_characters = re.sub(r'[ -~]', '', dictionary_entry_on_yomi[0].find_all('span')[0].text.replace('\n', ''))
    ks_radical = list(radical_characters)[0]
    ks_radical_variants = list(radical_characters)[1:]
    ks_radical_meaning = [entry.lstrip() for entry in dictionary_entry_on_yomi[0].find_all('span')[1].text
                          .replace('\n', '').replace('  ', '').split(',')]
    ks_parts_list = dictionary_entry_on_yomi[1].find_all('a')
    ks_parts = [entry.text for entry in ks_parts_list]
    try:
        ks_kanji_variants = [entry.text for entry in page_soup.find(class_='dictionary_entry variants').find_all('a')]
    except AttributeError:
        ks_kanji_variants = ''
    ks_meanings = page_soup.find(class_='kanji-details__main-meanings').text \
        .replace('\n', '').replace('  ', '').split(', ')
    dictionary_entry_kun_yomi = page_soup.find_all(class_='dictionary_entry kun_yomi')
    try:
        ks_kun_list = dictionary_entry_kun_yomi[0].find_all('a')
        ks_kun = [entry.text.replace('Kun:', '') for entry in ks_kun_list]
    except IndexError:
        ks_kun = ''
    if page_soup.find(class_='row compounds').find_all(class_='small-12 large-6 columns'):
        ks_comp = page_soup.find(class_='row compounds').find_all(class_='small-12 large-6 columns')
        if 'On reading compounds' in ks_comp[0].text:
            ks_on_comp = [entry.text.replace('\n', '').replace('  ', '') for entry in ks_comp[0].find_all('li')]
            try:
                ks_kun_comp = [entry.text.replace('\n', '').replace('  ', '') for entry in ks_comp[1].find_all('li')]
            except IndexError:
                ks_kun_comp = ''
        elif 'Kun reading compounds' in ks_comp[0].text:
            ks_kun_comp = [entry.text.replace('\n', '').replace('  ', '') for entry in ks_comp[0].find_all('li')]
            try:
                ks_on_comp = [entry.text.replace('\n', '').replace('  ', '') for entry in ks_comp[1].find_all('li')]
            except IndexError:
                ks_on_comp = ''
    try:
        ks_on_list = dictionary_entry_on_yomi[2].find_all('a')
        ks_on = [entry.text.replace('On:', '') for entry in ks_on_list]
    except IndexError:
        ks_on = ''
    try:
        ks_grade = page_soup.find(class_='grade').text.replace('\n', '').replace('  ', '')
    except AttributeError:
        ks_grade = ''
    try:
        ks_jlpt = page_soup.find(class_='jlpt').text.replace('\n', '').replace(' ', '').replace('JLPTlevel', '')
    except AttributeError:
        ks_jlpt = ''
    try:
        ks_frequency = page_soup.find(class_='frequency').text.replace('\n', '').split(' of')[0]
    except AttributeError:
        ks_frequency = ''
    try:
        ks_nanori = page_soup.find(class_='dictionary_entry nanori').find('dd').text.replace('\n', '').split('、 ')
    except AttributeError:
        ks_nanori = ''
    return ks_character, ks_strokes, ks_radical, ks_radical_variants, ks_radical_meaning, ks_parts, ks_kanji_variants, \
        ks_meanings, ks_kun, ks_on, ks_grade, ks_jlpt, ks_frequency, ks_on_comp, ks_kun_comp, ks_nanori


def save_data(sd_kanji):
    kanji_data = {
        'character': character,
        'strokes': strokes,
        'radical': radical,
        'radical variants': radical_variants,
        'radical meaning': radical_meaning,
        'parts': parts,
        'kanji_variants': kanji_variants,
        'meanings': meanings,
        'kun': kun,
        'on': on,
        'nanori readings': nanori,
        'grade': grade,
        'jlpt': jlpt,
        'frequency': frequency,
        'on reading compounds': on_comp,
        'kun reading compounds': kun_comp
    }
    with open('data/kanji_data/' + directory + '/' + sd_kanji + '.json', 'w') as json_file:
        json.dump(kanji_data, json_file, ensure_ascii=False)


kanji_category_list = [line.rstrip('\n') for line in open('data/kanji_category_list.txt')]
for category in kanji_category_list:
    directory = category.replace('%23kanji %23', '').replace(':', '%3A')
    kanji_list = [line.rstrip('\n') for line in
                  open('data/kanji_data/' + directory + '/' + directory + '_kanji_list.txt')]
    for kanji in kanji_list:
        print("\nSearching Jisho.org for: '" + kanji + "'")
        search_data = []
        character, strokes, radical, radical_variants, radical_meaning, parts, kanji_variants, meanings, kun, on, \
            grade, jlpt, frequency, on_comp, kun_comp, nanori = kanji_search(kanji)
        save_data(kanji)
