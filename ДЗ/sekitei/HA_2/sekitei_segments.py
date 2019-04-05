import sys
import os
import re
import random
import time
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.linear_model import LogisticRegression
#import urllib.parse as urlparse
import urlparse
import urllib
import numpy as np


features_list = None
clusters = None
quota_by_cluster = None


def add_feature(features, str):
    features[str] += 1


def get_features(features, line):
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



def extract_features(all_features, url_features, urls):
    for url in urls:
        features = Counter()
        get_features(features, url)
        all_features += features
        url_features.append(features)

    return all_features



def make_features_matrix(all_features, url_features):
    X = np.zeros((len(url_features), len(all_features)))
    for i, _ in enumerate(url_features):
        for j, key in enumerate(all_features.keys()):
            X[i][j] += url_features[i][key]
    return X

def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
    global features_list 
    global clusters 
    global quota_by_cluster 

    url_features = list()
    all_features = Counter()
    #N_URLS = len(QLINK_URLS) + len(UNKNOWN_URLS)
    n_clusters = 7
    N_URLS = 500
    alpha = 0.03        
    frequency = N_URLS * alpha        

    all_features = extract_features(all_features, url_features, QLINK_URLS)
    all_features = extract_features(all_features, url_features, UNKNOWN_URLS)

    for key, value in list(all_features.items()):
        if value < frequency:
            del all_features[key]

    features_list = all_features

    X = np.zeros((len(url_features), len(all_features)))
    X = make_features_matrix(all_features, url_features)


    #clusters = KMeans(10, init='k-means++', max_iter=300, n_jobs=-1)
    clusters = MiniBatchKMeans(n_clusters=n_clusters)
    clusters.fit(X)
    label = clusters.predict(X)

    unique, counts = np.unique(label[:len(QLINK_URLS)], return_counts=True)
    x_qlinks = dict(zip(unique, counts))
    quota_cluster = np.zeros(10).astype(int)

    for i in x_qlinks:
        quota_cluster[i] = int(float(x_qlinks[i]) / len(QLINK_URLS) * QUOTA)

    quota_by_cluster = quota_cluster



def fetch_url(url):
    global features_list 
    global clusters 
    global quota_by_cluster 

    features = Counter()
    get_features(features, url)
    url_feature = list()
    url_feature.append(features)
    X = make_features_matrix(features_list, url_feature)

    clust = clusters.predict(X)

    if quota_by_cluster[clust] > 0:
        quota_by_cluster[clust] -= 1
        return True
    else:
        return False
