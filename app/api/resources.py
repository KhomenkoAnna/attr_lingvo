"""
REST API Resource Routing
http://flask-restplus.readthedocs.io
"""

import logging
from copy import deepcopy
from collections import Counter

from flask import request
from flask_restplus import Resource

from app.api.utils.Text import Text, IPM_MULTIPLIER
from app.api.utils.correlation import pearson_correlation, calculate_ngrams_correlation, prepare_arrays, \
    linear_regression, jaccard_correlation, student_correlation, calculate_score
from . import api_rest

logger = logging.getLogger()


@api_rest.route('/results/calculate')
class Calculate(Resource):

    def post(self):
        json_payload = request.json
        # logger.info(f'Received json payload: {json_payload}')

        attributes = {k: v for k, v in json_payload['attributes'].items() if v['checked'] is True}
        first_text_results, first_text_debug, first_text_keywords, first_text_bigrams, first_text_trigrams, first_text_intensifiers = Text(
            json_payload['first_text'],
            json_payload['first_text_genre'],
            attributes,
            json_payload['normal_form']).calculate_results()
        second_text_results, second_text_debug, second_text_keywords, second_text_bigrams, second_text_trigrams, second_text_intensifiers = Text(
            json_payload['second_text'],
            json_payload['second_text_genre'],
            attributes,
            json_payload['normal_form']).calculate_results()

        first_array, second_array = prepare_arrays(list(map(lambda k: k[1]['result'], first_text_results.items())),
                                                   list(map(lambda k: k[1]['result'], second_text_results.items())))

        pearson_coefficient = pearson_correlation(first_array, second_array)
        linear_regression_coefficient = linear_regression(first_array, second_array)
        jaccard_coefficient = jaccard_correlation(first_array, second_array)
        student_coefficient = student_correlation(first_array, second_array)

        if first_text_keywords or second_text_keywords:
            keywords_correlation = calculate_ngrams_correlation(
                first_text_keywords,
                second_text_keywords
            )
        else:
            keywords_correlation = None

        if first_text_bigrams or second_text_bigrams:
            bigrams_correlation = calculate_ngrams_correlation(
                first_text_bigrams,
                second_text_bigrams
            )
        else:
            bigrams_correlation = None

        if first_text_trigrams or second_text_trigrams:
            trigrams_correlation = calculate_ngrams_correlation(
                first_text_trigrams,
                second_text_trigrams
            )
        else:
            trigrams_correlation = None

        if first_text_intensifiers or second_text_intensifiers:
            intensifiers_correlation = calculate_ngrams_correlation(
                first_text_intensifiers,
                second_text_intensifiers
            )
        else:
            intensifiers_correlation = None

        payload = {
            'pearson_correlation': pearson_coefficient,
            'linear_regression': linear_regression_coefficient,
            'jaccard_correlation': jaccard_coefficient,
            'student_correlation': student_coefficient,
            'keywords_correlation': keywords_correlation,
            'bigrams_correlation': bigrams_correlation,
            'trigrams_correlation': trigrams_correlation,
            'intensifiers_correlation': intensifiers_correlation,
            'attributes': [{'id': ind,
                            'description': v['name'],
                            'name': k,
                            'first_text': round(v['result'], 4) if type(v['result']) is not str else v['result'],
                            'second_text': round(second_text_results[k]['result'], 4) if type(
                                second_text_results[k]['result']) is not str else second_text_results[k]['result']
                            } for ind, (k, v) in enumerate(first_text_results.items(), start=1)],
            'extended_attributes': [{'id': ind, 'description': v['description'], 'name': k,
                                     'first_text': {
                                         'value': round(v['value'], 4) if type(v['value']) is not str else v['value'],
                                         'debug': v['debug']},
                                     'second_text': {'value': round(second_text_debug[k]['value'], 4) if type(
                                         second_text_debug[k]['value']) is not str else second_text_debug[k][
                                         'value'],
                                                     'debug': second_text_debug[k]['debug']}
                                     } for ind, (k, v) in enumerate(first_text_debug.items(), start=1)],
        }
        logger.info(f'Results: {payload}')
        return {'results': payload}, 200


EXTENDED_PERMANENT_ATTRIBUTES = ('total_sentences',
                                 'total_words',
                                 'total_syllables',
                                 'total_complex_words',
                                 'total_nouns',
                                 'total_pronouns',
                                 'total_adjectives',
                                 'total_verbs',
                                 'total_verb_forms',
                                 'total_adverbs',
                                 'total_prepositions',
                                 'total_conjunctions',
                                 )
PERMANENT_ATTRIBUTES = ('flesch_kincaid_index',
                        'fog_index',
                        'avg_word_len',
                        'avg_sentence_len',
                        'sentence_len8_count',
                        'pr_coefficient',
                        'qu_coefficient',
                        'ac_coefficient',
                        'din_coefficient',
                        'con_coefficient',)


@api_rest.route('/results/recalculate')
class Recalculate(Resource):

    def post(self):
        json_payload = request.json

        extended_attributes = []
        for attribute in json_payload['extended_attributes']:
            extended_attribute = deepcopy(attribute)
            if attribute['name'] not in EXTENDED_PERMANENT_ATTRIBUTES:
                extended_attribute['first_text']['debug'] = list(
                    filter(lambda x: not x[1], attribute['first_text']['debug']))
                extended_attribute['first_text']['value'] = len(extended_attribute['first_text']['debug'])
                extended_attribute['second_text']['debug'] = list(
                    filter(lambda x: not x[1], attribute['second_text']['debug']))
                extended_attribute['second_text']['value'] = len(extended_attribute['second_text']['debug'])
            extended_attributes.append(extended_attribute)

        first_text_total_words = next(
            (attr['first_text']['value'] for attr in extended_attributes if attr['name'] == 'total_words'))
        second_text_total_words = next(
            (attr['second_text']['value'] for attr in extended_attributes if attr['name'] == 'total_words'))
        attributes = []
        for attribute in json_payload['attributes']:
            relative_attribute = deepcopy(attribute)
            if attribute['name'] not in PERMANENT_ATTRIBUTES:
                relative_attribute['first_text'] = (next((attr['first_text']['value'] for attr in extended_attributes if
                                                          attr['name'] == attribute[
                                                              'name'])) / first_text_total_words) * IPM_MULTIPLIER
                relative_attribute['second_text'] = (next(
                    (attr['second_text']['value'] for attr in extended_attributes if
                     attr['name'] == attribute['name'])) / second_text_total_words) * IPM_MULTIPLIER
            attributes.append(relative_attribute)

        first_array, second_array = prepare_arrays(list(map(lambda k: k['first_text'], attributes)),
                                                   list(map(lambda k: k['second_text'], attributes)))

        pearson_coefficient = pearson_correlation(first_array, second_array)
        linear_regression_coefficient = linear_regression(first_array, second_array)
        jaccard_coefficient = jaccard_correlation(first_array, second_array)
        student_coefficient = student_correlation(first_array, second_array)

        first_text_keywords = dict(next((map(lambda x: (x[0], x[2]), attr['first_text']['debug'])
                                         for attr in extended_attributes if attr['name'] == 'keywords_count'),
                                        []))
        second_text_keywords = dict(next((map(lambda x: (x[0], x[2]), attr['second_text']['debug'])
                                          for attr in extended_attributes if attr['name'] == 'keywords_count'),
                                         []))
        if first_text_keywords or second_text_keywords:
            keywords_correlation = calculate_ngrams_correlation(
                first_text_keywords,
                second_text_keywords
            )
        else:
            keywords_correlation = None

        first_text_bigrams = dict(next((map(lambda x: (x[0], x[2]), attr['first_text']['debug'])
                                        for attr in extended_attributes if attr['name'] == 'bigrams_count'),
                                       []))
        second_text_bigrams = dict(next((map(lambda x: (x[0], x[2]), attr['second_text']['debug'])
                                         for attr in extended_attributes if attr['name'] == 'bigrams_count'),
                                        []))
        if first_text_bigrams or second_text_bigrams:
            bigrams_correlation = calculate_ngrams_correlation(
                first_text_bigrams,
                second_text_bigrams
            )
        else:
            bigrams_correlation = None

        first_text_trigrams = dict(next((map(lambda x: (x[0], x[2]), attr['first_text']['debug'])
                                        for attr in extended_attributes if attr['name'] == 'trigrams_count'),
                                       []))
        second_text_trigrams = dict(next((map(lambda x: (x[0], x[2]), attr['second_text']['debug'])
                                         for attr in extended_attributes if attr['name'] == 'trigrams_count'),
                                        []))

        if first_text_trigrams or second_text_trigrams:
            trigrams_correlation = calculate_ngrams_correlation(
                first_text_trigrams,
                second_text_trigrams
            )
        else:
            trigrams_correlation = None

        first_text_intensifiers = dict(next((Counter(map(lambda x: x[2], attr['first_text']['debug']))
                                        for attr in extended_attributes if attr['name'] == 'intensifiers_count'),
                                       []))
        second_text_intensifiers = dict(next((Counter(map(lambda x: x[2], attr['second_text']['debug']))
                                        for attr in extended_attributes if attr['name'] == 'intensifiers_count'),
                                       []))

        if first_text_intensifiers or second_text_intensifiers:
            intensifiers_correlation = calculate_ngrams_correlation(
                calculate_score(first_text_intensifiers, first_text_total_words),
                calculate_score(second_text_intensifiers, second_text_total_words)
            )
        else:
            intensifiers_correlation = None

        payload = {
            'pearson_correlation': pearson_coefficient,
            'linear_regression': linear_regression_coefficient,
            'jaccard_correlation': jaccard_coefficient,
            'student_correlation': student_coefficient,
            'keywords_correlation': keywords_correlation,
            'bigrams_correlation': bigrams_correlation,
            'trigrams_correlation': trigrams_correlation,
            'intensifiers_correlation': intensifiers_correlation,
            'attributes': attributes,
            'extended_attributes': extended_attributes,
        }
        logger.info(f'Results: {payload}')
        return {'results': payload}, 200
