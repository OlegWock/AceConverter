#!/usr/bin/env python3.4
#-*- coding: UTF-8 -*-

ficbook_to_fb2_genders = {'Гет': 'love',
                          'Романтика': 'love',
                          'Юмор': 'humor' ,
                          'Драма': 'dramaturgy',
                          'Фэнтези': 'sf_fantasy',
                          'Фантастика': 'sf',
                          'Мистика': 'sf_horror',
                          'Детектив': 'detective' ,
                          'Экшн (action)': 'det_action',
                          'Психология': 'sci_psychology',
                          'Философия': 'sci_philosophy',
                          'Ужасы': 'sf_horror' ,
                          'PWP': 'love_erotica',
                          'Стихи': 'poetry',
                          'Статьи': 'ref_ref'}
                          
text_formating_tags_replace = {'<b>': '<strong>',
                               '</b>': '</strong>',
                               '<i>': '<emphasis>',
                               '</i>': '</emphasis>',
                               '<s>': '<strikethrough>',
                               '</s>': '</strikethrough>',
                               '<center>': '<subtitle>',
                               '</center>': '</subtitle>',
                               '<p align="right" style="margin: 0px;">': '',
                               '</p>': ''
                                }
                                

                          
                          
template_doc = """<?xml version="1.0" encoding="utf-8"?>
<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0"
  xmlns:l="http://www.w3.org/1999/xlink">
  <description>
  {title_info}
  {doc_info}
  </description>
    {body}
</FictionBook>
"""

##################################################################################################################
##################################################################################################################


tem_title_info = """<title-info>
   {genders}
   <author>
   <first-name>{author_nickname}</first-name>
    <nickname>{author_nickname}</nickname>
   </author>
   <book-title>{book_title}</book-title>
   <annotation>
    <p>{annotation}</p>
   </annotation>
   <lang>ru</lang>
   <src-lang>ru</src-lang>
  </title-info>
"""

tem_doc_info = """<document-info>
   <author>
    <nickname>Fic2fb2 program</nickname>
   </author>
   <program-used>Fic2fb2</program-used>
   <date value="{date_year}-{date_month}-{date_day}">{date_year}-{date_month}-{date_day}</date>
   <id>FicBook-fanfic-{fanfic_id}-Fic2fb2</id>
   <version>1.1</version>
   <history>
     <p>1.0 - книга создана с помощью Fic2fb2</p>
   </history>
  </document-info>
"""

##################################################################################################################

tem_body = """<body>
  <title><p>{fandom}:</p><p>{fanfic_name}</p></title>
  {sections}
</body>
"""
                          
                          
##################################################################################################################
##################################################################################################################

