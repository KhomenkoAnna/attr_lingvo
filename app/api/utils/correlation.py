import numpy as np
import math
import scipy.stats
from scipy import stats
from sklearn.metrics import jaccard_score

from app.api.utils.ngrams import log_likelihood
from app.api.utils.Text import NAN_ELEMENT


def prepare_arrays(first_array, second_array):
    first_array_wo_nan, second_array_wo_nan = [], []
    # filter our pair where at least one element is 'N/A'
    for (el1, el2) in zip(first_array, second_array):
        if el1 is NAN_ELEMENT or el2 is NAN_ELEMENT:
            continue
        first_array_wo_nan.append(round(el1, 4))
        second_array_wo_nan.append(round(el2, 4))
    return first_array_wo_nan, second_array_wo_nan


def pearson_correlation(first_array, second_array):
    if not first_array or not second_array:
        return 'N/A'
    return round(np.corrcoef(first_array, second_array)[0, 1], 2)


def linear_regression(first_array, second_array):
    if not first_array or not second_array:
        return {'pvalue': 'N/A',
                'rvalue': 'N/A',
                'slope': 'N/A',
                'stderr': 'N/A',
                'intercept': 'N/A'}
    result = scipy.stats.linregress(first_array, second_array)
    return {'pvalue': round(result.pvalue, 2),
            'rvalue': round(result.rvalue, 2),
            'slope': round(result.slope, 2),
            'stderr': round(result.stderr, 2),
            'intercept': round(result.intercept, 2)}


def jaccard_correlation(first_array, second_array):
    # return jaccard_score(first_array, second_array)
    return 'N/A'


def student_correlation(first_array, second_array):
    if not first_array or not second_array:
        return {'pvalue': 'N/A',
                'statistic': 'N/A'}
    result = stats.ttest_ind(first_array, second_array)
    return {'pvalue': round(result.pvalue, 2),
            'statistic': round(result.statistic, 2)}


def calculate_ngrams_correlation(first_keywords, second_keywords):
    first_array, second_array = [], []
    for key in first_keywords.keys() | second_keywords.keys():
        first_array.append(first_keywords.get(key, 0))
        second_array.append(second_keywords.get(key, 0))
    result = round(np.corrcoef(first_array, second_array)[0, 1], 2)
    return 'n/a' if math.isnan(result) else result


def calculate_score(intensifiers, total_words):
    intensifiers_score = {}
    for word in intensifiers:
        ll_score = log_likelihood(word, intensifiers[word], total_words)
        intensifiers_score[word] = ll_score
    return intensifiers_score
