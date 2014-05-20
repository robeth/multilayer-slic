'''
Created on Apr 15, 2014

Function form of create_model.py

@author: fruity
'''

import numpy as np
from sklearn.metrics import confusion_matrix, accuracy_score
from constant import array_px_path, train_start_index, train_end_index, test_start_index, test_end_index, classifier_path_px, classifier_extension, category 
from os import listdir, makedirs
from os.path import isfile, join, splitext, exists
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.cross_validation import StratifiedKFold, cross_val_score

def create_model(scenario):
    n_layer = scenario['layer']
    n_column = 12 * n_layer + 1
    target_directory = array_px_path + scenario['codename'] + "/"
    
    def get_usable_index():
        n_feature = 12
        n_used_feature = 8
        indexes = []
        current = 0
        for i in range(n_layer):
            indexes += range(current,current+n_used_feature)
            current += n_feature
        return indexes
    
    indexes = get_usable_index()
    
    target_files = [ f for f in listdir(target_directory) if isfile(join(target_directory,f)) ]
    target_train_files = target_files[train_start_index: train_end_index]
    target_test_files = target_files[test_start_index: test_end_index]
    
    X = np.zeros((0,n_column))
    X_test = np.zeros((0, n_column))
    
    for target_file in target_train_files:
#         print target_directory+target_file
        entry = np.load(target_directory+target_file)
        X = np.concatenate((X,entry), axis = 0 )
    
    for target_file in target_test_files:
#         print target_directory+target_file
        entry = np.load(target_directory+target_file)
        X_test = np.concatenate((X_test,entry), axis = 0 )
        
    Y = X[:, -1]
    X = X[:,indexes]
    
    Y_test = X_test[:, -1]
    X_test = X_test[:,indexes]
    
    strat_kfold = StratifiedKFold(Y, n_folds = 5)
#     print "Train data: test data = %s : %s"%(len(X), len(X_test))
    # clf1 = svm.SVC(class_weight='auto')
    # clf2 = DecisionTreeClassifier()
    clf3 = RandomForestClassifier()
    
    def benchmark(classifier, X, Y, train_indices, test_indices):
        classifier.fit(X[train_indices], Y[train_indices])
        Y_predict = classifier.predict(X[test_indices])
        return accuracy_score(Y[test_indices], Y_predict), confusion_matrix(Y[test_indices], Y_predict)
        
    highest_accuracy = 0
    highest_counter = 0
    chosen_train_index = []
    chosen_test_index = []
    counter = 0
    
    
    for train_index, test_index in strat_kfold:
        acc, conf = benchmark(clf3, X, Y, train_index, test_index)
        if acc > highest_accuracy:
            highest_accuracy = acc
            highest_counter = counter
            chosen_train_index = train_index
            chosen_test_index = test_index
        counter += 1
#         new_entry = {'acc':acc, 'fn':conf[0,1], 'fp':conf[1,0]}
#         str_new_entry = str(new_entry) + " -- train-test:(%s,%s)"%(len(train_index), len(test_index)) 
#         print str_new_entry
    
        
    print "Chosen index-accuracy: %s -- %s"%(highest_counter, highest_accuracy)
    clf3.fit(X[chosen_train_index], Y[chosen_train_index])
    
    
    Y_predict = clf3.predict(X_test)
    a_score, c_matrix = accuracy_score(Y_test, Y_predict), confusion_matrix(Y_test, Y_predict)
    final_result = {'codename': scenario['codename'],'acc':a_score, 'fn':c_matrix[0,1], 'fp':c_matrix[1,0], 'tn':c_matrix[0,0], 'tp':c_matrix[1,1]}
    str_final_result = "Test result --> " + str(final_result) + " test case:"+str(len(X_test))
    print str_final_result

    classifier_directory = classifier_path_px + scenario['codename'] + "/"
    if not exists(classifier_directory):
        makedirs(classifier_directory)
    joblib.dump(clf3, classifier_directory+'RF'+"-"+category+"-"+scenario['codename']+ classifier_extension)
    return final_result