# coding: utf-8


import sys
import os
import re
import random
import time
#from sklearn.cluster import <any cluster algorithm>
import numpy as np
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import urlparse
import urllib


#sekitei = None;

all_features = None
clust = None
quota_cluster = None


# sekitei.all_features / ._clust  / ._quota_cluster
class sekitei:
    pass

# plus_one, add_features --> add_feature, get_features

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


def extract_useful_features(all_features, N, alpha=0.025):
	for key, value in list(all_features.items()):
		if value < N*alpha:
			del all_features[key]

	return all_features

def make_features_matrix(all_features, url_features):
    X = np.zeros((len(url_features), len(all_features)))
    for i, _ in enumerate(url_features):
        for j, key in enumerate(all_features.keys()):
            X[i][j] += url_features[i][key]
    return X




# extract_features, extract_useful_features, make_features_matrix
def define_segments(QLINK_URLS, UNKNOWN_URLS, QUOTA):
	url_features = list()
	all_features = Counter()
	N_URLS = len(QLINK_URLS) + len(UNKNOWN_URLS)

	all_features = extract_features(all_features, url_features, LINK_URLS)
	all_features = extract_features(all_features, url_features, UNKNOWN_URLS)

	all_features = extract_useful_features(all_features, N_URLS)

	#global all_features
	sekitei._all_features = all_features

	X = np.zeros((len(url_features), len(all_features)))

	#for i, _ in enumerate(url_features):
     #   for j, key in enumerate(all_features.keys()):
      #      X[i][j] += url_features[i][key]

	X = make_features_matrix(all_features, url_features)

	sekitei._clust = KMeans(10, init='k-means++', max_iter=300, n_jobs=-1)
    sekitei._clust.fit(X)
    label = sekitei._clust.predict(X)

    unique, counts = np.unique(label[:len(QLINK_URLS)], return_counts=True)
    x_qlinks = dict(zip(unique, counts))
    quota_cluster = np.zeros(10).astype(int)
    for i in x_qlinks:
        quota_cluster[i] = int(float(x_qlinks[i]) / len(QLINK_URLS) * QUOTA)
    sekitei._quota_cluster = quota_cluster


    #print "define_segments is not implemented";


#
# returns True if need to fetch url
#
def fetch_url(url):
    features = Counter()
    get_features(features, url)
    url_features = list()
    url_features.append(features)

    X = make_features_matrix(sekitei._all_features, url_feature)
	#X = np.zeros((len(url_features), len(all_features)))

	#for i, _ in enumerate(url_features):
     #   for j, key in enumerate(all_features.keys()):
      #      X[i][j] += url_features[i][key]

	clust = sekitei._clust.predict(X)

    if sekitei._quota_cluster[clust] > 0:
        sekitei._quota_cluster[clust] -= 1
        return True
    else:
        return False
    #global sekitei
    #return sekitei.fetch_url(url);
    #return True;
