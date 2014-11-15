#!/usr/bin/env python3.4
#-*- coding: UTF-8 -*-

import requests as req
import lxml.html as html
import re

import datetime
import hashlib
from zipfile import ZipFile

from PyQt4 import QtCore, QtGui, uic
import sys, os

import fb2templates as fb2
import epubtemplates as epub

ratings = ['/ratings/g','/ratings/pg13' ,'/ratings/r' ,'/ratings/nc17' ,'/ratings/nc21']
    
genders_list = ['Гет', 'Джен', 'Слэш (яой)', 'Фемслэш (юри)', 
               'Романтика', 'Ангст', 'Юмор', 'Флафф', 'Драма',
               'Фэнтези', 'Фантастика', 'Мистика', 'Детектив', 
               'Экшн (action)', 'Психология', 'Философия', 
               'Пародия', 'Повседневность', 'Даркфик', 'Ужасы', 
               'PWP', 'POV', 'Hurt/comfort', 'AU', 'Songfic', 
               'Мифические существа', 'Эксперимент', 
               'ER (Established Relationship)', 
               'Занавесочная история', 'Злобный автор', 'Стёб', 
               'Стихи', 'Статьи', 'Омегаверс', 'Учебные заведения']
               
warings_list = ['BDSM', 'Смерть персонажа', 'OOC', 'Насилие', 
                'Изнасилование', 'Инцест', 'Твинцест', 
                'Нецензурная лексика', 'Групповой секс', 
                'Мэри Сью (Марти Стью)', 'ОМП', 'ОЖП', 
                'Underage', 'Кинк', 'Мужская беременность', 
                'Секс с использованием посторонних предметов', 
                'Зоофилия', 'Некрофилия', 'Смена пола (gender switch)']

replace_not_window_charters = ('/', '\\', ':', '*', '?', '"', '<', '>', '|')

cookies = None
mode = None
fb2_or_epub = None
dwn_url = None

log = open('log.txt', 'w')

class MainWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        uic.loadUi('main.ui', self)
                
def wrlog(txt):
    global log
    log.write(txt + '\n')
    log.flush()
    print(txt)


def check404(page):
    if '<div class="cat_404"></div>' in page.text:
        return True
    else:
        return False

def checkColecttionIsOpen(doc):
    if doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/p/b/text()') and doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/p/b/text()')[0] == 'Сборник является личным, для Вас доступ к нему запрещен.':
        return False
    else:
        return True

def login():
  try:
     global cookies
     text, ok = QtGui.QInputDialog.getText(None, "Введите логин",
                "Введите логин", QtGui.QLineEdit.Normal)
     if ok and text != '':
        login = text
     text, ok = QtGui.QInputDialog.getText(None, "Введите пароль", "Введите пароль", QtGui.QLineEdit.Normal)
     if ok and text != '':
        password = text
     # Составляем словарь с данными и отправляем запрос
     data = {"login":login, "password":password, "do_login":"submit", "remember":"on"}
     wrlog('Пытаюсь авторизироваться как %s' % login)
     r = req.post('http://ficbook.net/', data)
     # Если авторизировались -- генерируем и возращаем куки, иначе -- возвращаем False
     if '<a href="/home" title="Рабочий кабинет" class="user_home">' in r.text:
         md5_pass = hashlib.new('md5')
         md5_pass.update(password.encode('utf-8'))
         cookies = {'login':login,'md5_pass': md5_pass.hexdigest()}
         QtGui.QMessageBox.information(None, 'Успех', 
        'Yep. Авторизация прошла успешно.')
         window.login.setText('Авторизация\n({})'.format(login))
         wrlog('Успешно авторизировался как %s' % login)
         return True
     else:
        QtGui.QMessageBox.information(None, 'Error', 
        'Авторизация не удалась.')
        wrlog('Авторизация провалена')
        return False
  except Exception as e:
     showErrorMessage(e)


def getAuthorFics(url):
  try:
    wrlog('Начинаю скачивать фанфики автора %s' % url)
    # Все фанфики одного автора
    fics = [] # будущий список фанфиков
    counter = 1 # счетчик страниц
    while True:
        r = req.get(url + "?show=author&p=" + str(counter)) 
        doc = html.document_fromstring(r.text)
        # Если на странице есть блок с работами.
        # Это обусловленно тем, что фикбук не выдает 404 если загрузить страницу под несоществуючим номером
        # Она просто будет пустой
        if not doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[2]/blockquote[5]/table/tr[1]/td/a/@href') and not doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[2]/blockquote[4]/table/tr/td/a/@href'):
            break
        # Список ссылок на фанфики с текущей страницы
        cur_page_fics = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[2]/blockquote[5]/table/tr[1]/td/a/@href')
        cur_page_fics += doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[2]/blockquote[4]/table/tr[1]/td/a/@href')
        for fic in cur_page_fics:
            fics.append("http://ficbook.net" +fic)
        counter += 1
    return fics
  except Exception as e:
    showErrorMessage(e)

def getCollectionFics(url):
  try:
    wrlog('Начинаю скачивать фанфики со сборника %s' % url)
    # Все фанфики с одного зборника
    fics = [] # будущий список фанфиков
    counter = 1 # счетчик страниц
    r = req.post(url, cookies = cookies) 
    doc = html.document_fromstring(r.text)
    if checkColecttionIsOpen(doc):
        while True:
            r = req.get(url + "?sort=author&p=" + str(counter), cookies=cookies) 
            doc = html.document_fromstring(r.text)
            # Если на странице есть блок с фиками.
            # Это обусловленно тем, что фикбук не выдает 404 если загрузить страницу под несоществуючим номером
            # Она просто будет пустой
            if not doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div/table/tr/td[1]/table/tr[1]/td/*'):
                break
            # Список ссылок на фанфики с текущей страницы
            cur_page_fics = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div/table/tr/td[1]/table/tr[1]/td/a/@href')
            for fic in cur_page_fics:
               fics.append("http://ficbook.net" + fic)
            counter += 1
    else:
        wrlog("Закрытый сборник. URL: %s" % url)
        QtGui.QMessageBox.information(None, 'Ошибка', 'Сборник является приватным. Если это ваш сборник, или вы имеете к нему доступ -- авторизируйтесь.')
        return

    return fics
  except Exception as e:
    showErrorMessage(e)

def getListOfLinks(path):
  try:
    wrlog('Получаю список ссылок из файла %s' % path)
    # А эта функция просто читает файл и делает из него список ссылок
    f = open(path, 'r')
    fics = f.read().split('\n')
    f.close()
    return fics
  except Exception as e:
    showErrorMessage(e)

def getFanficInfo(url):
  try:
    ffinfo = {}
    r = req.get(url)
    if not check404(r):
        doc = html.document_fromstring(r.text)
        # Тут все предельно ясно: получаем нужную инфу путем извлечения ее через xpath
        ffinfo['id'] = url[url.find('ficbook.net/readfic/')+20:]
        ffinfo['name'] = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/h1[1]/text()')[0].strip()
        ffinfo['author'] = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/a[1]/text()')[0]
        ffinfo['authorlink'] = 'http://ficbook.net' + doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/a[1]/@href')[0]
        ffinfo['likes'] = int(doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/div[1]/div[1]/text()')[0].strip().replace('+',''))
        ffinfo['description'] = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[2]/span[1]/text()')[0].strip()       
        warings = []
        genders = []
        # Разделение на жанры и предупреждения.
        # Не знаю зачем оно, но пусть будет.
        genders_buf = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/a')
        for g in genders_buf:
            try:
                href = g.attrib['href']
                title = g.attrib['title']
            except KeyError:
                continue
            if not href in ratings and href.startswith('/ratings/'):
                title = title[3:title.find('</b>')]
                if title in genders_list:
                    genders.append(title)
                elif title in warings_list:
                    warings.append(title)
        ffinfo['genders'] = genders
        ffinfo['warings'] = warings
        # А тут фэндом, размер и рейтинг
        # ------------------------------- 
        # -- Дайте один NC, пожалуйста.
        # -- Вам оридж или по Лаки Стар?
        # -- А по ЛС какие жанры?
        # -- Только юри.
        # -- Ахуеть, дайте два!
        # ------------------------------- 
        buf_list = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/a')
        for item in buf_list:
            buf_link = '/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/table/tr/td[1]/a[@href = "' + str(item.get('href')) + '"]'
            if doc.xpath(buf_link + '/text()'):
                value = doc.xpath(buf_link + '/text()')[0] .strip()
            if '/fanfiction/' in str(item.get('href')):
                ffinfo['fandom'] = value
            elif str(item.get('href')) in ratings:
                ffinfo['rating'] = value
            elif '/sizes/' in str(item.get('href')):
                ffinfo['size'] = value
        
        if doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div[@class="part_list"]'):
            parts = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div[@class="part_list"]/a/@href')
            parts_urls = list(map(lambda x: 'http://ficbook.net' + x.replace('#part_content', ''), parts))
        else:
            parts_urls = [url]

        ffinfo['parts'] = parts_urls
        return ffinfo
    else:
        QtGui.QMessageBox.information(None, 'Error 404', 
        'Такой страницы не существует.')

  except Exception as e:
    showErrorMessage(e)

def downloadFic(parts):
  try:
    wrlog('\n=====================================\nНачинаю скачивать фанфик.')
    dwnloaded = []
    for url in parts:
        wrlog('Скачиваю часть. По URL: %s' % url)
        r = req.get(url)
        doc = html.document_fromstring(r.text)
        if doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div[@class="part_text urlize"]/h2/text()'):
            part_name = doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div[@class="part_text urlize"]/h2/text()')[0]
        else:
            part_name = '...'

        #если включена публичная бета, то в блоке на один div больше, а по классам, не отличишь, 
        # следовательно, нужно проверять включена ли бета для этого фанфика
        if doc.xpath('/html/body/table[2]/tr[2]/td[1]/table/tr[2]/td[2]/div[@class="part_text urlize"]/div[@class="public_beta"]'):
            div_to_find = '<div class="public_beta">'
        else:
            div_to_find = '<div class="public_beta_disabled">'
        part_raw_text = r.text[r.text.find(div_to_find)+len(div_to_find): r.text.find("</div>", r.text.find(div_to_find))]
        dwnloaded.append([part_name, part_raw_text.strip()])
        wrlog('Часть успешно скачана.')
    wrlog('Фанфик успешно скачан.')
    return dwnloaded
  except Exception as e:
    showErrorMessage(e)

def convertToFb2(ffinfo, parts_list):
  try:
    # Конвертация в fb2
    # Нужен словарь с инфой о фанфике и список состоящий из частей
    formated_parts = []
    to_title_info = {}
    to_title_info['genders'] = ''
    for g in ffinfo['genders']:
        if g in fb2.ficbook_to_fb2_genders:
            to_title_info['genders'] += "<genre>{}</genre>\n".format(fb2.ficbook_to_fb2_genders[g])
    to_title_info['author_nickname'] = ffinfo['author']
    to_title_info['book_title'] = ffinfo['name']
    to_title_info['annotation'] = ffinfo['description']

    title_info = fb2.tem_title_info.format(**to_title_info)

    to_doc_info = {}
    to_doc_info['date_year'] = datetime.datetime.now().timetuple()[0]
    to_doc_info['date_day'] = datetime.datetime.now().timetuple()[2]
    to_doc_info['date_month'] = datetime.datetime.now().timetuple()[1]
    to_doc_info['fanfic_id'] = ffinfo['id']

    doc_info = fb2.tem_doc_info.format(**to_doc_info)
    dl = downloadFic(ffinfo['parts'])
    t_o = re.compile('<\\w+>')
    t_c = re.compile('</\\w+>')
    for index, p in enumerate(dl):
        # Заменяем HTML-теги на fb2-теги
        for rep in fb2.text_formating_tags_replace:
            dl[index][1] = dl[index][1].replace(rep, fb2.text_formating_tags_replace[rep])
        buf = dl[index][1]
        buf = buf.strip()   
        # Разделяем текст на части по переводу строки. Нужно для того, что бы при нескольких пеереводах строки подряд
        # разметка не сбивалась 
        buf = buf.split('<br />')    
        # И склеиваем их, превращая в абзацы книги
        correct = []

        for st in buf:
            new_str = st
            opened = t_o.findall(st)
            closed = t_c.findall(st)
            for tag in closed:
                if '<' + tag[2:] in opened:
                    del closed[closed.index(tag)]
                    del opened[opened.index('<' + tag[2:])]
            for tag in closed[::-1]:
                new_str = '<' + tag[2:] + new_str
            if not new_str.strip():
                continue
            part_doc = html.fromstring(new_str)
            correct.append(html.tostring(part_doc).decode("UTF-8"))

			

        correct = '</p><p>'.join(correct)
        correct = '<section>\n<title><p>{}</p></title><p>'.format(p[0]) + correct + '</p></section>'
        formated_parts.append(correct)
    to_body_info = {}
    to_body_info['fandom'] = ffinfo['fandom']
    to_body_info['fanfic_name'] = ffinfo['name']
    to_body_info['sections'] = '\n'.join(formated_parts)

    body = fb2.tem_body.format(**to_body_info)

    full_book = fb2.template_doc.format(**{'title_info': title_info, 'doc_info': doc_info, 'body': body})

    filename = '{} - {}.fb2'.format(ffinfo['author'], ffinfo['name'])
    for rep in replace_not_window_charters:
        filename = filename.replace(rep, ' ') 

    with open('books/' + filename, 'w', encoding='UTF-8') as f:
        f.write(full_book)
  except Exception as e:
    showErrorMessage(e)

def convertToEpub(ffinfo, parts_list):
    to_opf = {'title': ffinfo['name'], 'url': 'ficbook.net/readfic/' + ffinfo['id'], 'description': ffinfo['description'], 
              'author': ffinfo['author'], 'datetime': '{0}-{1}-{2}'.format(*datetime.datetime.now().timetuple()),
              'items': '', 'itemrefs': ''}

    to_ncx = {'name': ffinfo['name'], 'author': ffinfo['author'], 'url': 'ficbook.net/readfic/' + ffinfo['id'], 'navMap': ''}

    filename = '{} - {}.epub'.format(ffinfo['author'], ffinfo['name'])
    for rep in replace_not_window_charters:
        filename = filename.replace(rep, ' ') 
    arc = ZipFile('books/' + filename, 'w')
    #####################################################
    with open('styles.css', 'w', encoding='UTF-8') as f:
        f.write(epub.css)
    arc.write('styles.css')
    os.remove('styles.css')

    with open('mimetype', 'w', encoding='UTF-8') as f:
        f.write(epub.mimetype)
    arc.write('mimetype')
    os.remove('mimetype')

    with open('container.xml', 'w', encoding='UTF-8') as f:
        f.write(epub.container)
    arc.write('container.xml', 'META-INF/container.xml')
    os.remove('container.xml')

    #####################################################
    counter = 1
    for title, text in parts_list:
        with open('chapter{}.html'.format(counter), 'w', encoding='UTF-8') as f:
            f.write(epub.page.format(**{'ff_name': ffinfo['name'], 'part_name': title, 'text': text}))
        arc.write('chapter{}.html'.format(counter))
        to_opf['items'] += epub.item.format(**{'chapter_no': counter}) + '\n'
        to_opf['itemrefs'] += epub.itemref.format(**{'chapter_no': counter}) + '\n'
        to_ncx['navMap'] += epub.navPoint.format(**{'chapter_no': counter, 'chapter_name': title}) + '\n'
        os.remove('chapter{}.html'.format(counter))
        counter += 1

    with open('book.opf', 'w', encoding='UTF-8') as f:
        f.write(epub.book_opf.format(**to_opf))
    arc.write('book.opf')
    os.remove('book.opf')

    with open('book.ncx', 'w', encoding='UTF-8') as f:
        f.write(epub.book_ncx.format(**to_ncx))
    arc.write('book.ncx')
    os.remove('book.ncx')



def startDwn(md):
    mode = md
    if window.to_fb2.isChecked():
        fb2_or_epub = 'fb2'
    elif window.to_ePub.isChecked():
        fb2_or_epub = 'epub'
    if md == 'author':
        text, ok = QtGui.QInputDialog.getText(None, "Введите ссылку",
                "Введите ссылку на профиль автора", QtGui.QLineEdit.Normal)
        if ok and text != '':
            dwn_url = text
            try:
                fics = getAuthorFics(dwn_url)
                counter = 1
                for fic in fics:
                    wrlog('Получаю информацию о фанфике. Прогресс: {}/{}'.format(counter, len(fics)))
                    info = getFanficInfo(fic)
                    wrlog('Скачиваю фанфик. Прогресс: {}/{}'.format(counter, len(fics)))
                    prt = downloadFic(info['parts'])
                    wrlog('Перепаковываю фанфик в файл.')
                    if fb2_or_epub == 'fb2':
                        convertToFb2(info, prt)
                    elif fb2_or_epub == 'epub':
                        convertToEpub(info, prt)
                    counter += 1
                wrlog('Конвертация закончена.')
                window.status.setText('Конвертация закончена.')
            except Exception as e:
                showErrorMessage(e)


    elif md == 'collection':
        text, ok = QtGui.QInputDialog.getText(None, "Введите ссылку",
                "Введите ссылку на сборник", QtGui.QLineEdit.Normal)
        if ok and text != '':
            dwn_url = text
            try:
                fics = getCollectionFics(dwn_url)
                if not fics:
                    return
                counter = 1
                for fic in fics:                    
                    info = getFanficInfo(fic)
                    prt = downloadFic(info['parts'])
                    if fb2_or_epub == 'fb2':
                        convertToFb2(info, prt)
                    elif fb2_or_epub == 'epub':
                        convertToEpub(info, prt)
                    counter += 1
                wrlog('Конвертация закончена.')
                window.status.setText('Конвертация закончена.')
            except Exception as e:
                showErrorMessage(e)

                
    elif md == 'single':
        text, ok = QtGui.QInputDialog.getText(None, "Введите ссылку",
                "Введите ссылку на фанфик", QtGui.QLineEdit.Normal)
        if ok and text != '':
            dwn_url = text
            try:
                wrlog('Собираю информацию о фанфике')
                info = getFanficInfo(dwn_url)
                wrlog('Скачиваю фанфик')
                prt = downloadFic(info['parts'])
                wrlog('Перепаковываю фанфик в файл.')
                if fb2_or_epub == 'fb2':
                    convertToFb2(info, prt)
                elif fb2_or_epub == 'epub':
                    convertToEpub(info, prt)
                window.status.setText('Конвертация закончена.')
                wrlog('Конвертация закончена.')
            except Exception as e:
                showErrorMessage(e)


    elif md == 'list':
        path = QtGui.QFileDialog.getOpenFileName(None, "Открыть файл", 
                                            '', 'Все файлы (*);;Текстовые файлы (*.txt)')
        if path:
            dwn_url = path
            try:
                fics = getListOfLinks(dwn_url)
                counter = 1
                for fic in fics:
                    info = getFanficInfo(fic)
                    prt = downloadFic(info['parts'])
                    if fb2_or_epub == 'fb2':
                        convertToFb2(info, prt)
                    elif fb2_or_epub == 'epub':
                        convertToEpub(info, prt)
                    counter += 1
                window.status.setText('Конвертация закончена.')
            except Exception as e:
                showErrorMessage(e)


    

def aboutBox():
    QtGui.QMessageBox.information(None, 'О программе', 
        'AceConverter -- это программа, которая поможет вам сконвертировтаь фанфик(и) с сайта <a href="ficbook.net">ficbook.net</a> в fb2- или ePub-книгу. Доступна функция конвертации всех фанфиков автора, всех фанфиков со сборника, всех фанфиков со списка (текстовый файл) или конвертация одного фанфика по ссылке. Приятного использования! Если вы желаете поддержать автора или у вас есть вопросы -- загляните сюда: <a href="https://vk.com/olegwock_public">vk.com/olegwock_public</a>' )


def showErrorMessage(error):
    wrlog(str(error))
    QtGui.QMessageBox.information(None, 'Error', 
        'Произошла ошибка, пожалуйста, сообщите о ней автору приложив файл log.txt в папке с программой.')
    


app = QtGui.QApplication(sys.argv)

window = MainWindow()
clipboard = app.clipboard()

QtCore.QObject.connect(window.about, QtCore.SIGNAL('clicked()'), aboutBox)
QtCore.QObject.connect(window.login, QtCore.SIGNAL('clicked()'), login)
QtCore.QObject.connect(window.author, QtCore.SIGNAL('clicked()'), lambda: startDwn('author'))
QtCore.QObject.connect(window.collection, QtCore.SIGNAL('clicked()'), lambda: startDwn('collection'))
QtCore.QObject.connect(window.from_file, QtCore.SIGNAL('clicked()'), lambda: startDwn('list'))
QtCore.QObject.connect(window.link, QtCore.SIGNAL('clicked()'), lambda: startDwn('single'))

try:
    os.mkdir('books')
except Exception:
    pass
window.show()
sys.exit(app.exec_())

