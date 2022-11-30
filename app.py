from email import header
from http import cookies
from flask import Flask, render_template, request, redirect, url_for, send_file, make_response
import pandas as pd
import requests
import re
import time
import os

app = Flask(__name__)


CORPORA = [
    ['evk', 'http://gisly.net/corpus/', 'Evenki'],
    ['ady', 'http://adyghe.web-corpora.net/adyghe_corpus/', 'Adyghe'],
    ['neo', 'http://neo-aramaic.web-corpora.net/urmi_corpus/', 'Neo-Aramaic'],
    ['tur', 'http://neo-aramaic.web-corpora.net/turoyo_corpus/', 'Turoyo'],
    ['ckt', 'https://chuklang.ru/', 'Chukchi'],
    ['alb', 'http://albanian.web-corpora.net/albanian_corpus/', 'Albanian'],
    ['dgr', 'https://linghub.ru/digor_ossetic_flex_corpus/', 'Digor Ossetic'],
    ['iro', 'https://linghub.ru/iron_ossetic_flex_corpus/', 'Iron Ossetic'],
    ['tjk', 'https://tajik-corpus.org/tajik_corpus/', 'Tajik'],
    ['dlg', 'https://inel.corpora.uni-hamburg.de/DolganCorpus/', 'Dolgan'],
    ['erz', 'http://erzya.web-corpora.net/erzya_corpus/', 'Erzya Main'],
    ['erm','http://erzya.web-corpora.net/erzya_social_media/', 'Erzya Social Media'],
    ['mmr', 'http://meadow-mari.web-corpora.net/meadow-mari_corpus/', 'Meadow Mari Main'],
    ['mmm', 'http://meadow-mari.web-corpora.net/meadow-mari_social_media/', 'Meadow Mari Social Media'],
    ['mok', 'http://moksha.web-corpora.net/moksha_corpus/', 'Moksha'],
    ['mom', 'http://moksha.web-corpora.net/moksha_social_media/', 'Moksha Social Media'],
    ['kms', 'https://inel.corpora.uni-hamburg.de/KamasCorpus/', 'Kamas'],
    ['kmz', 'http://komi-zyrian.web-corpora.net/komi-zyrian_corpus/', 'Komi-Zyrian Main'],
    ['kmm', 'http://komi-zyrian.web-corpora.net/komi-zyrian_social_media/', 'Komi-Zyrian Social Media'],
    ['slk', 'https://inel.corpora.uni-hamburg.de/SelkupCorpus/', 'Selkup'],
    ['udm', 'http://udmurt.web-corpora.net/udmurt_corpus/', 'Udmurt Main'],
    ['umm', 'http://udmurt.web-corpora.net/udmurt_social_media/', 'Umdumrt Social Media'],
    ['uds', 'http://udmurt.web-corpora.net/sound_aligned_udmurt_corpus/', 'Udmurt Sound Aligned'],
    ['bsm', 'http://multimedia-corpus.beserman.ru/', 'Beserman'],
    ['brt', 'http://buryat.web-corpora.net/buryat_corpus/', 'Buryat'],
    ['wct', 'https://linghub.ru/wc_corpus/', 'WC corpus']

]

COOKIES = {}

@app.route('/')
def main_page():
    print("BEFORE main_page()")
    sessions = []
    for corpus in CORPORA:
        # print(corpus)
        cookies = requests.get(corpus[1] + 'get_word_fields').cookies.get_dict()
        sessions.append(cookies)
        COOKIES[corpus[0]] = list(cookies)[0]
    
    resp = make_response(render_template('index.html', langs=[[x[0], x[2]] for x in CORPORA]))
    
    for i, cookie in enumerate(sessions):
        resp.set_cookie(f'{list(cookie)[0]}_{CORPORA[i][0]}', list(cookie.values())[0])
        resp.set_cookie(f'{CORPORA[i][0]}_page', '1')
    print("AFTER main_page(), result = ", resp)
    return resp

@app.route('/get_word_fields')
def empty():
    print("BEFORE empty()")
    result = ''
    print("AFTER empty(), result = ", result)
    return result


@app.route('/search_sent')
def search():
    print("BEFORE search()")

    langs_corp = request.args.getlist('languages')

    if not langs_corp:
        langs_corp = [x[0] for x in CORPORA]

    bases = [f'{x[1]}search_sent?' for x in CORPORA if x[0] in langs_corp]
    query = request.url.split('search_sent?', maxsplit=1)[1]
    sessions = request.cookies

    langs = [x[2] for x in CORPORA if x[0] in langs_corp]
    header = [f'<button class="tablinks" id="header_{lang}" onclick="openLang(event, \'{lang}\')">{lang}</button>' for lang in langs]
    header = '\n'.join(header)
    header = f'<div class="tab"> {header} </div>'

    body = []
    print(COOKIES)
    for i, base in enumerate(bases):
        body.append(f'<div id="{langs[i]}" class="tabcontent">' +\
            re.sub(
                r'data-page="(\d+)"',
                f'data-page="{langs_corp[i]}_\g<1>"',
                requests.get(base + query, cookies={COOKIES[langs_corp[i]]: sessions[f'{COOKIES[langs_corp[i]]}_{langs_corp[i]}']}).text
                ) +\
                '</div>')
    
    active = f'<div id="active" style="display: none;">{langs[0]}_1</div>'
    active_langs = '$@'.join(langs_corp)
    print(active_langs)
    active_langs = f'<div id="active_langs" style="display: none;">active_langs={active_langs}</div>'

    result = active_langs + active + header + ''.join(body)
    print("AFTER search(), result = ", result)
    return result


@app.route('/search_sent/<page>')
def pagination(page):
    print("BEFORE pagination(), page = ", page)
    lang, page = page.split('_')
    corpus = [x for x in CORPORA if x[0] == lang][0]
    base = corpus[1] + 'search_sent/'
    session = request.cookies.get(f'{COOKIES[lang]}_{lang}')

    body = re.sub(
        r'data-page="(\d+)"',
        f'data-page="{lang}_\g<1>"',
        requests.get(base + page, cookies={COOKIES[lang]: session}).text
        )
    active = f'<div id="active" style="display: none;">{corpus[2]}</div>'
    result = active + body
    print("AFTER pagination(), page = ", page, ", result = ", result)
    return result


@app.route('/static/img/search_in_progress.gif')
def wip():
    print('BEFORE wip()')
    result = send_file('static/img/search_in_progress.gif')
    print('AFTER wip()')
    return result


if __name__ == '__main__':
    app.run(debug=True)
