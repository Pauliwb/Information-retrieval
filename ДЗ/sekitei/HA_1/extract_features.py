# coding: utf-8

import sys
import re
import random
from operator import itemgetter
import urlparse
import urllib
#from urllib.parse  import unquote
from string import digits
from collections import Counter




# Функция, которая отбирает N случайных урлов с сайта
def random_url(file_path, N_URLS):
    urls = list()

    with open(file_path) as f:
        for line in f:
            urls.append(line)
    random.shuffle(urls)

    res = urls[:N_URLS]
    return res


def add_feature(features, name):
    features.setdefault(name, 0)
    features[name] += 1


def get_features(features, urls):
    for line in urls:
        line = line.strip('\n')
        line = urlparse.urlparse(line)
        index = 0

        for segment in urllib.unquote(line.path).split('/'):
            if segment == '':
                continue

            add_feature(features, 'segment_name_{0}:{1}'.format(index, segment))
            add_feature(features, 'segment_len_{0}:{1}'.format(index, len(segment)))

            if segment.isdigit():
                add_feature(features, 'segment_[0-9]_{0}:1'.format(index))

            if re.match(r'[^\d]+\d+[^\d]', segment):
                add_feature(features, 'segment_substr[0-9]_{0}:1'.format(index))

            if re.match(r'.+[.]\w+', segment):
                ext = re.findall(r'.+[.](\w+)', segment)[0]
                add_feature(features, 'segment_ext_{0}:{1}'.format(index, ext))

            if re.match(r'[^\d]+\d+[^\d]', segment) and re.match(r'.+[.]\w+', segment):
                ext = re.findall(r'.+[.](\w+)', segment)[0]
                add_feature(features, 'segment_ext_substr[0-9]_{0}:{1}'.format(index, ext))

            index += 1

        add_feature(features, 'segments:{0}'.format(index))

        parameters = urllib.unquote(line.params).split('&')
        if parameters[0] != '':
            for param in parameters:
                add_feature(features, 'param:{0}'.format(param))
                add_feature(features, 'param_name:{0}'.format(param.split('=')[0]))



def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    #______Name_features_______#
    
    # 1. Количество сегментов в пути: segments = {}
    
    # 2. Список имен параметров запросной части (может быть пустым): param_name = {}
    
    # 3. Присутствие в запросной части пары < 𝑝𝑎𝑟𝑎𝑚𝑒𝑡𝑒𝑟𝑠 = 𝑣𝑎𝑙𝑢𝑒 > 𝑝𝑎𝑟𝑎𝑚 ∶< 𝑝𝑎𝑟𝑎𝑚𝑒𝑡𝑒𝑟𝑠 = 𝑣𝑎𝑙𝑢𝑒 > : param = {}
    
    # 4. Сегмент пути на позиции:
    # (a) Совпадает со значением < строка >
    #segment_name = {}
    # (b) Состоит из цифр
    #segment_0_9 = {}
    # (c) < строка с точностью до комбинации цифр >
    #segment_substr_0_9 = {}
    # (d) Имеет заданное расширение
    #segment_ext = {}
    # (e) Комбинация из двух последних вариантов
    #segment_ext_substr_0_9 = {}
    # (f) Состоит из данного количества символов:
    #segment_len = {}

    #___________________________#
    
    
    N_URLS = 2000
    #alpha = 0.2  # Не проходит тесты
    alpha = 0.1        
    frequency = N_URLS * alpha        
    features_dict = dict()

    Qlink = open(INPUT_FILE_1, "r")          # 2000 q_links
    all_links = open(INPUT_FILE_2, "r")        # 20 000 всех urls


    get_features(features_dict, random_url(INPUT_FILE_1, N_URLS))
    get_features(features_dict, random_url(INPUT_FILE_2, N_URLS))

    features_dict = dict(sorted(features_dict.items(), key=lambda x:-x[1]))

    with open(OUTPUT_FILE, 'w') as out:
        for i in features_dict:
            if features_dict[i] > frequency:
                out.write(str(i)+'\t'+str(features_dict[i])+'\n')


    Qlink.close()
    all_links.close()

 #print >> sys.stderr, "Not implemented"
