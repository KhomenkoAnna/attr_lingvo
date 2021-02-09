import os
import math
from functools import reduce

import nltk
from nltk.probability import *

STOPWORDS = {'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она',
'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне',
'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли',
'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там',
'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их',
'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто',
'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее',
'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над',
'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем',
'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю',
'между'}

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPENCORPORA_KEYWORDS = {}

with open(os.path.join(ROOT_DIR + '/data/1grams-3.txt'), encoding='utf-8') as f:
    for line in f:
        key, value = line.split()
        OPENCORPORA_KEYWORDS[value] = int(key)

OPENCORPORA_KEYWORDS_TOTAL = sum((v for k, v in OPENCORPORA_KEYWORDS.items()))


def log_likelihood(word, freq, total_words):
    a = freq
    b = OPENCORPORA_KEYWORDS.get(word, 0)
    c = total_words
    d = OPENCORPORA_KEYWORDS_TOTAL
    E1 = c * (a+b) / (c+d)
    E2 = d * (a+b) / (c+d)
    G2 = 0
    if a > 0:
        G2 += 2 * a * math.log(a/E1)
    if b > 0:
        G2 += 2 * b * math.log(b/E2)

    return round(G2 * math.copysign(1, a/c - b/d), 2)


def create_bigrams(parsed_sentences):
    bigrams = nltk.bigrams((word[1].normal_form for sent in parsed_sentences for word in sent
                            if len(word[1].normal_form) > 2 and word[1].normal_form not in STOPWORDS))
    bigrams_freq = nltk.FreqDist(bigrams).most_common()
    return bigrams_freq[:100]


def create_trigrams(parsed_sentences):
    trigrams = nltk.trigrams((word[1].normal_form for sent in parsed_sentences for word in sent
                            if len(word[1].normal_form) > 2 and word[1].normal_form not in STOPWORDS))
    trigrams_freq = nltk.FreqDist(trigrams).most_common()
    return trigrams_freq[:100]
