# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 18:11:35 2016

@author: Swaroop
"""

import csv
import matplotlib.pyplot as plt
import pickle
import sys
from numpy import mean
from sklearn import cross_validation
from sklearn.metrics import accuracy_score, precision_score, recall_score ,f1_score
sys.path.append("../tools/")

from feature_format import featureFormat
from feature_format import targetFeatureSplit

from sklearn.feature_selection import SelectKBest

def remove_keys(dict_object, keys):
    """ removes a list of keys from a dict object """
    for key in keys:
        dict_object.pop(key, 0)

def get_k_best(data_dict, features_list, k):
    """ runs scikit-learn's SelectKBest feature selection
        returns dict where keys=features, values=scores
    """
    data = featureFormat(data_dict, features_list)
    labels, features = targetFeatureSplit(data)

    k_best = SelectKBest(k=k)
    k_best.fit(features, labels)
    scores = k_best.scores_
    unsorted_pairs = zip(features_list[1:], scores)
    sorted_pairs = list(reversed(sorted(unsorted_pairs, key=lambda x: x[1])))
    k_best_features = dict(sorted_pairs[:k])
    print "{0} best features: {1}\n".format(k, k_best_features.keys())
    return k_best_features
    
def add_networth(data_dict, features_list):
    """ mutates data dict to add aggregate values from stocks and salary """
    fields = ['total_stock_value', 'exercised_stock_options', 'salary']
    for record in data_dict:
        emp = data_dict[record]
        is_valid = True
        for field in fields:
            if emp[field] == 'NaN':
                is_valid = False
        if is_valid:
            emp['networth'] = sum([emp[field] for field in fields])
        else:
            emp['networth'] = 'NaN'
    features_list += ['networth']

def add_email_features(data_dict, features_list):
    """ mutates data dict to add aggregate values from stocks and salary """
    fraction_from_poi_email=dict_to_list(data_dict,"from_poi_to_this_person","to_messages")
    fraction_to_poi_email=dict_to_list(data_dict,"from_this_person_to_poi","from_messages")
    count=0
    for i in data_dict:
        data_dict[i]["fraction_from_poi_email"]=fraction_from_poi_email[count]
        data_dict[i]["fraction_to_poi_email"]=fraction_to_poi_email[count]
        count +=1
    features_list += ['fraction_from_poi_email'] 
    features_list += ['fraction_to_poi_email'] 
def visualize(data_dict, feature_x, feature_y):
    """ generates a plot of feature y vs feature x, colors poi """

    data = featureFormat(data_dict, [feature_x, feature_y, 'poi'])

    for point in data:
        x = point[0]
        y = point[1]
        poi = point[2]
        color = 'red' if poi else 'blue'
        plt.scatter(x, y, color=color)
    plt.xlabel(feature_x)
    plt.ylabel(feature_y)
    plt.show()
    
def dict_to_list(data_dictionary,key,normalizer):
    new_list=[]

    for i in data_dictionary:
        if data_dictionary[i][key]=="NaN" or data_dictionary[i][normalizer]=="NaN":
            new_list.append(0.)
        elif data_dictionary[i][key]>=0:
            new_list.append(float(data_dictionary[i][key])/float(data_dictionary[i][normalizer]))
    return new_list

def evaluate_clf(clf, features, labels, num_iters=1000, test_size=0.3):
    print clf
    accuracy = []
    precision = []
    recall = []
    f1score =[]
    first = True
    for trial in range(num_iters):
        features_train, features_test, labels_train, labels_test =\
            cross_validation.train_test_split(features, labels, test_size=test_size,random_state=42)
        clf.fit(features_train, labels_train)
        predictions = clf.predict(features_test)
        accuracy.append(accuracy_score(labels_test, predictions))
        precision.append(precision_score(labels_test, predictions))
        recall.append(recall_score(labels_test, predictions))
        f1score.append(f1_score(labels_test, predictions))
        if trial % 10 == 0:
            if first:
                sys.stdout.write('\nProcessing')
            sys.stdout.write('.')
            sys.stdout.flush()
            first = False

    print "done.\n"
    print "precision: {}".format(mean(precision))
    print "recall:    {}".format(mean(recall))
    print "F1Score:    {}".format(mean(f1score))
    return mean(precision), mean(recall)