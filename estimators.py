from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, ElasticNet, Lasso, Ridge, LassoLars
# from keras.wrappers.scikit_learn import KerasRegressor
# from mlp_model import make_model
from config import *
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.gaussian_process.kernels import RBF
import numpy as np
import time

C = np.arange(1, 1001, 100)


def svm_hyper_param_space(est_type):
    svm_hps = {'kernel': ['linear', 'rbf'],
               'C': C,
               'gamma': ['scale', 'auto']}

    if est_type == 'reg':
        svm_hps['epsilon'] = [0.3, 0.5, 0.7, 0.9]

    return svm_hps


def mlp_hyper_param_space(num_samples, est_type):

    mlp_hps = {'hidden_layer_sizes': [[int(num_samples*1.5), int(num_samples*0.7)],
                                      #[int(num_samples*2), int(num_samples)],
                                      [int(num_samples*2.5), int(num_samples*1.3)]],
               'activation': ['logistic', 'relu'],
               #'learning_rate': ['constant'],
               'solver': ['adam'],
               #'momentum': [0.6, 0.7, 0.8, 0.9],
               'momentum': [0.9],
               'warm_start': [True],
               'early_stopping': [True],
               #'power_t': [0.3, 0.4, 0.5, 0.6, 0.7],
               #'max_iter': np.arange(150, 301, 50),
               'max_iter': [500],
               #'beta_1': [0.6, 0.7, 0.8, 0.9],
               'beta_1': [0.5],
               #'beta_2': [0.85, 0.89, 0.95, 0.999],
               'batch_size': [4]}

    if est_type == 'reg':
        mlp_hps['activation'].append('tanh')

    return mlp_hps


# return best regressors in a list with order rfr, svmr, mlpr, lr, enr, rr, lasr, laslarr
def regress(feat_frame_train, y_train, cv_folds, performance_metric, normType_train):

    t0 = time.time()

    num_samples = feat_frame_train.shape[0]
    num_feats = feat_frame_train.shape[1]
    reg_params = []
    reg_all = []

    alpha = np.arange(1, 5)*0.1

    # Random Forest Regression
    rfr_hyper_param_space = {'n_estimators': np.arange(50, 201, 50)}
    reg_params.append([RandomForestRegressor(), rfr_hyper_param_space, regType_list[0]])


    # SVM Regression
    svmr_hyper_param_space = svm_hyper_param_space('reg')
    reg_params.append([SVR(cache_size=1000, max_iter=10000), svmr_hyper_param_space, regType_list[1]])


    # MLP Regression
    mlpr_hyper_param_space = mlp_hyper_param_space(num_samples, 'reg')
    reg_params.append([MLPRegressor(), mlpr_hyper_param_space, regType_list[2]])


    # Linear Regression
    lr_hyper_param_space = {}
    reg_params.append([LinearRegression(), lr_hyper_param_space, regType_list[3]])


    # ElasticNet Regression
    # enr_hyper_param_space = {'l1_ratio': np.arange(0, 11)*0.1,
    #                          'max_iter': [2000],
    #                          'precompute': ['auto']}
    # reg_params.append([ElasticNet(), enr_hyper_param_space, regType_list[4]])

    # Ridge Regression
    rr_hyper_param_space = {'alpha': alpha}
    reg_params.append([Ridge(), rr_hyper_param_space, regType_list[5]])


    # Lasso Regression
    lasr_hyper_param_space = {'alpha': alpha}
    reg_params.append([Lasso(), lasr_hyper_param_space, regType_list[6]])


    # LassoLARS Regression
    laslarr_hyper_param_space = {'alpha': alpha}
    reg_params.append([LassoLars(), laslarr_hyper_param_space, regType_list[7]])

    for reg_p in reg_params:
        print("Running GridSearch with %s" % reg_p[2])
        reg_all.append([GridSearchCV(reg_p[0], param_grid=reg_p[1], n_jobs=-1, scoring=performance_metric,
                                     cv=cv_folds, verbose=1, iid=True).fit(feat_frame_train, np.ravel(y_train)),
                        reg_p[2],
                        normType_train,
                        num_feats])
    print("!!!!!!!!!!!!!!!!!!!!!!!!REGRESSION TOOK %.2f seconds" % (time.time()-t0))
    return reg_all


# return best classifiers in a list with order rfc, svmc, mlpc, abc, logr, knc, gpc, gnb, lda, qda
def classify(feat_frame_train, y_train, cv_folds, performance_metric, normType_train):

    t0 = time.time()

    num_samples = feat_frame_train.shape[0]
    num_feats = feat_frame_train.shape[1]
    clr_params = []
    clr_all = []

    # Random Forest Classification
    rfc_hyper_param_space = {'n_estimators': np.arange(50, 201, 50),
                             'warm_start': [True]}
    clr_params.append([RandomForestClassifier(), rfc_hyper_param_space, clrType_list[0]])

    # SVM Classification
    svmc_hyper_param_space = svm_hyper_param_space('clr')
    clr_params.append([SVC(cache_size=1000, max_iter=10000), svmc_hyper_param_space, clrType_list[1]])

    # MLP Classification
    mlpc_hyper_param_space = mlp_hyper_param_space(num_samples, 'clr')
    clr_params.append([MLPClassifier(), mlpc_hyper_param_space, clrType_list[2]])

    # Adaboost Classification
    # abc_hyper_param_space = {'n_estimators': np.arange(50, 101, 10),
    #                         'learning_rate': [0.0001, 0.001, 0.01, 0.1, 0.15, 0.2, 0.25, 0.3]}
    # clr_params.append([AdaBoostClassifier(), abc_hyper_param_space, clrType_list[3]])

    # Logistic Regression
    logr_hyper_param_space = {'penalty': ['l2'],
                              'multi_class': ['ovr', 'multinomial'],
                              'solver': ['newton-cg', 'sag', 'lbfgs'],
                              'warm_start': [True],
                              'C': C,
                              'class_weight': ['balanced'],
                              'max_iter': [10000]}
    if feat_frame_train.shape[0] <= feat_frame_train.shape[1]:
        logr_hyper_param_space['dual'] = [True]
    clr_params.append([LogisticRegression(), logr_hyper_param_space, clrType_list[4]])

    # KNeighbors Classification
    knc_hyper_param_space = {'n_neighbors': [3, 5, 7],
                             'weights': ['uniform', 'distance'],
                             'algorithm': ['auto'],
                             'p': [2]}
    clr_params.append([KNeighborsClassifier(), knc_hyper_param_space, clrType_list[5]])

    # # Gaussian Processes Classification
    # gpc_hyper_param_space = {'kernel': ['linear', RBF(1.0)],
    #                          'n_restarts_optimizer': [0, 1, 2],
    #                          'multi_class': ['one_vs_rest'],
    #                          'warm_start': [True]}
    # clr_params.append([GaussianProcessClassifier(), gpc_hyper_param_space, clrType_list[6]])

    # Gaussian Naive Bayes Classification
    gnb_hyper_param_space = {#'priors': [0.10, 0.15, 0.60, 0.15],
                             }
    clr_params.append([GaussianNB(), gnb_hyper_param_space, clrType_list[7]])

    # Linear Discriminant Analysis
    lda_hyper_param_space = {'solver': ['svd'],
                             #'shrinkage': ['auto'],
                             #'priors': np.array([0.10, 0.15, 0.60, 0.15]),
                            }
    clr_params.append([LinearDiscriminantAnalysis(), lda_hyper_param_space, clrType_list[8]])

    # # Quadratic Discriminant Analysis
    # qda_hyper_param_space = {'priors': np.array([0.10, 0.15, 0.60, 0.15]),
    #                          'reg_param': [0.0, 0.1]}
    # clr_params.append([QuadraticDiscriminantAnalysis(), qda_hyper_param_space, clrType_list[9]])

    for clr_p in clr_params:
        print("Running GridSearch with %s" % clr_p[2])
        clr_all.append([GridSearchCV(clr_p[0], param_grid=clr_p[1], n_jobs=-1, scoring=performance_metric,
                                     cv=cv_folds, verbose=1, iid=True).fit(feat_frame_train, np.ravel(y_train)),
                        clr_p[2],
                        normType_train,
                        num_feats])
    print("!!!!!!!!!!!!!!!!!!!!!!!!CLASSIFICATION TOOK %.2f seconds" % (time.time()-t0))
    return clr_all