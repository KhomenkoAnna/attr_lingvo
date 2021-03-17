import pickle
import re
from collections import OrderedDict

import nltk
from nltk.tokenize import WordPunctTokenizer
import pymorphy2
import numpy as np
from flask import current_app
from pyaspeller import YandexSpeller

from app.api.rules.intensifiers import INTENSIFIERS_REGEX
from app.api.rules.interjections import INTERJECTIONS_REGEXP
from app.api.rules.intro_words import INTRO_WORDS_REGEXP
from app.api.rules.modal_particles import MODAL_PARTICLES_REGEX
from app.api.rules.rules import *
from app.api.utils.display_utils import highlight_match
from app.api.utils.morph_utils import parse_sentence_morph, MorphRegexConverter, match_morph, \
    parse_word_morph, tokenize_sentences, tokenize_corp_sentences, Match
from app.api.utils.ngrams import log_likelihood, create_bigrams, create_trigrams

NAN_ELEMENT = 'N/A'
VOWELS = 'ауоыиэяюёе'
IPM_MULTIPLIER = 1000000

SPELLER = YandexSpeller(lang='ru',
                        find_repeat_words=False,
                        ignore_digits=True,
                        ignore_latin=True,
                        ignore_roman_numerals=True,
                        ignore_uppercase=True,
                        ignore_urls=True,
                        )
STATES = ['STARTSYM', 'ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON',
                  'PROPN', 'PUNCT', 'SCONJ', 'SYM', 'VERB', 'ENDSYM']

ANNOTATION_DECIPHER = {
            'VERB': ['VERB', 'INFN', 'PRTF', 'PRTS', 'GRND'],
            'CCONJ': ['CONJ'],
            'SCONJ': ['CONJ'],
            'ADJ': ['ADJS', 'ADJF', 'COMP'],
            'NUM': ['NUMR', 'NUMB', 'intg', 'real'],
            'PRON': ['NPRO'],
            'DET': ['ADJS', 'ADJF'],
            'ADP': ['PREP'],
            'ADV': ['ADVB', 'PRED'],
            'INTJ': ['INTJ'],
            'PART': ['PRCL'],
            'PUNCT': ['PNCT'],
            'SYM': ['PNCT'],
            'NOUN': ['NOUN'],
            'PROPN': ['NOUN'],
            'AUX': ['VERB', 'PRCL']
        }

with open('./app/api/data/trans_probs.pickle', 'rb') as f:
    TRANS_PROBS = pickle.load(f)
with open('./app/api/data/emis_probs.pickle', 'rb') as f:
    EMIS_PROBS = pickle.load(f)
with open('./app/api/data/times_first_trans.pickle', 'rb') as f:
    TRANS_COUNTS = pickle.load(f)
with open('./app/api/data/times_emitted_from.pickle', 'rb') as f:
    EMIS_COUNTS = pickle.load(f)

MORPH_ANALYZER = pymorphy2.MorphAnalyzer()


class Text:
    def __init__(self, text, genre, attributes, normal_form):
        self.text = text
        self.attributes = attributes
        self.genre = genre
        self.normal_form = normal_form

        self.sentences = self.__tokenize_sentences()
        self.morph_parsed_sentences = [parse_sentence_morph(sentence) for sentence in self.sentences]
        self.morph_parsed_sentences_wo_punkt = self.__remove_punkt()
        self.total_words = self.__count_total_words()
        self.total_syllables, self.total_complex_words = self.__count_total_syllables()

        self.debug_available = self.total_words <= 30000

        self.total_nouns = 0
        self.total_pronouns = 0
        self.total_adjectives = 0
        self.total_verbs = 0
        self.total_verb_forms = 0
        self.total_adverbs = 0
        self.total_prepositions = 0
        self.total_conjunctions = 0

        self.__calculate_total_speech_parts()

        self.results = OrderedDict()
        self.extended_results = self.__create_extended_results()

    def __tokenize_sentences(self):
        if self.genre == 'corporate_correspondence':
            return tokenize_corp_sentences(self.text)
        else:
            return tokenize_sentences(self.text)

    def __remove_punkt(self):
        morph_parsed_sentences_wo_punkt = []
        for sentence in self.morph_parsed_sentences:
            morph_parsed_sentences_wo_punkt.append(
                [(word, parsed_word) for word, parsed_word in sentence if parsed_word and parsed_word.tag.POS])
        return morph_parsed_sentences_wo_punkt

    def __create_extended_results(self):
        return OrderedDict(
            {
                'total_sentences': {'value': len(self.sentences),
                                    'description': 'Количество предложений',
                                    'debug': None},
                'total_words': {'value': self.total_words,
                                'description': 'Количество слов',
                                'debug': None},
                'total_syllables': {'value': self.total_syllables,
                                    'description': 'Количество слогов',
                                    'debug': None},
                'total_complex_words': {'value': self.total_complex_words,
                                        'description': 'Количество слов длиной более 3-х слогов',
                                        'debug': None},
                'total_nouns': {'value': self.total_nouns,
                                'description': 'Количество существительных',
                                'debug': None},
                'total_pronouns': {'value': self.total_pronouns,
                                   'description': 'Количество местоимений',
                                   'debug': None},
                'total_adjectives': {'value': self.total_adjectives,
                                     'description': 'Количество прилагательных',
                                     'debug': None},
                'total_verbs': {'value': self.total_verbs,
                                'description': 'Количество глаголов',
                                'debug': None},
                'total_verb_forms': {'value': self.total_verb_forms,
                                     'description': 'Количество глагольных форм',
                                     'debug': None},
                'total_adverbs': {'value': self.total_adverbs,
                                  'description': 'Количество наречий',
                                  'debug': None},
                'total_prepositions': {'value': self.total_prepositions,
                                       'description': 'Количество предлогов',
                                       'debug': None},
                'total_conjunctions': {'value': self.total_conjunctions,
                                       'description': 'Количество союзов',
                                       'debug': None}
            }
        )

    def __count_total_words(self):
        return sum((len(sentence) for sentence in self.morph_parsed_sentences_wo_punkt))

    def __calculate_total_speech_parts(self):
        for sentence in self.morph_parsed_sentences_wo_punkt:
            for word, parsed_word in sentence:
                tag = str(parsed_word.tag.POS)
                if tag in ('NOUN',):
                    self.total_nouns += 1
                elif tag in ('NPRO',):
                    self.total_pronouns += 1
                elif tag in ('ADJF', 'ADJS'):
                    self.total_adjectives += 1
                elif tag in ('VERB', 'INFN'):
                    self.total_verbs += 1
                elif tag in ('ADVB',):
                    self.total_adverbs += 1
                elif tag in ('PRTF', 'PRTS', 'GRND'):
                    self.total_verb_forms += 1
                elif tag in ('PREP',):
                    self.total_prepositions += 1
                elif tag in ('CONJ',):
                    self.total_conjunctions += 1

    def __count_total_syllables(self):
        total_syllables = 0
        total_complex_words = 0
        for sentence in self.morph_parsed_sentences_wo_punkt:
            for word in sentence:
                word = word[0].lower()
                syllables_count = sum((1 for symbol in word if symbol in VOWELS))
                if syllables_count >= 3:
                    total_complex_words += 1
                total_syllables += syllables_count
        return total_syllables, total_complex_words

    def avg_word_len(self):
        # array of average word lengths for each sentence
        avg_word_len = []
        for sentence in self.morph_parsed_sentences_wo_punkt:
            try:
                avg_word_len.append(sum((len(word) for word, parsed_word in sentence)) / len(sentence))
            except ZeroDivisionError:
                pass
        return sum(avg_word_len) / len(self.sentences)

    def avg_sent_len_in_words(self):
        return self.total_words / len(self.sentences)

    def sentence_len8_count(self):
        """ Count of the sentences which length is more that 8 words in percents"""
        return (sum((1 for sentence in self.morph_parsed_sentences_wo_punkt if len(sentence) > 8)) / len(
            self.sentences)) * IPM_MULTIPLIER

    def flesch_kincaid_index(self):
        """ The Flesch–Kincaid readability tests are readability tests designed to indicate
         how difficult a passage in English is to understand """

        return 0.39 * (self.total_words / len(self.sentences)) + 11.8 * (
                self.total_syllables / self.total_words) - 15.59

    def fog_index(self):
        """ The Gunning fog index is a readability test.
         The index estimates the years of formal education a person needs to understand the text on the first reading """
        return 0.4 * (0.78 * self.avg_sent_len_in_words() + 100 * (self.total_complex_words / self.total_words))

    def pr_coefficient(self):
        try:
            return (self.total_nouns + self.total_pronouns) / (self.total_adjectives + self.total_verbs)
        except ZeroDivisionError:
            return NAN_ELEMENT

    def qu_coefficient(self):
        try:
            return (self.total_adjectives + self.total_pronouns) / (self.total_verbs + self.total_nouns)
        except ZeroDivisionError:
            return NAN_ELEMENT

    def ac_coefficient(self):
        try:
            return (self.total_verbs + self.total_verb_forms) / self.total_words
        except ZeroDivisionError:
            return NAN_ELEMENT

    def din_coefficient(self):
        try:
            return (self.total_verbs + self.total_verb_forms) / \
                   (self.total_nouns + self.total_adjectives + self.total_pronouns)
        except ZeroDivisionError:
            return NAN_ELEMENT

    def con_coefficient(self):
        return (self.total_prepositions + self.total_conjunctions) / len(self.sentences)

    def get_errors(self):
        try:
            errors = []
            errors_count = 0
            for i in range(0, len(self.sentences), 2000):
                error = list(
                    filter(lambda x: x['code'] in (1, 3), SPELLER.spell(' '.join(self.sentences[i: i + 2000]))))
                errors_count += len(error)
                if self.debug_available:
                    errors.extend(error)
            current_app.logger.info(f'Found errors: {errors if self.debug_available else errors_count}')
            self.extended_results['errors'] = {'value': errors_count,
                                               'description': 'Количество слов несловарного написания',
                                               'debug': list(map(lambda x: (x, False), errors)) if self.debug_available else None}
            return (errors_count / self.total_words) * IPM_MULTIPLIER
        except Exception as ex:
            current_app.logger.error(f'Exceptions trying to get/parse errors: {ex}')
            return NAN_ELEMENT

    def viterbi(self, tokens, states):
        matrix = []
        for i in range(len(tokens)):
            matrix.append([])
            if i == 0 or i == len(tokens) - 1:
                for j in range(len(states)):
                    matrix[i].append(0)
            else:
                for j in range(len(states)):
                    if j == 0 or j == len(states) - 1:
                        matrix[i].append(0)
                    else:
                        matrix[i].append({})
        matrix[0][0] = [1]
        matrix[-1][-1] = {}
        for i in range(1, len(matrix)):
            for j in range(len(matrix[i])):
                if matrix[i][j] != 0:
                    for k in range(len(matrix[i - 1])):
                        if matrix[i - 1][k] != 0:
                            if (states[k], states[j]) in TRANS_PROBS.keys() and (states[j], tokens[i]) in EMIS_PROBS.keys():
                                lst = matrix[i - 1][k] + [TRANS_PROBS[(states[k], states[j])]] + [EMIS_PROBS[(states[j], tokens[i])]]
                            elif (states[k], states[j]) in TRANS_PROBS.keys() and (states[j], tokens[i]) not in EMIS_PROBS.keys():
                                lst = matrix[i - 1][k] + [TRANS_PROBS[(states[k], states[j])]] + [1 / (125308 + EMIS_COUNTS[states[j]])]
                            elif (states[k], states[j]) not in TRANS_PROBS.keys() and (states[j], tokens[i]) in EMIS_PROBS.keys():
                                lst = matrix[i - 1][k] + [1 / (125308 + TRANS_COUNTS[states[k]])] + [EMIS_PROBS[(states[j], tokens[i])]]
                            elif (states[k], states[j]) not in TRANS_PROBS.keys() and (states[j], tokens[i]) not in EMIS_PROBS.keys():
                                lst = matrix[i - 1][k] + [1 / (125308 + TRANS_COUNTS[states[k]])] + [1 / (125308 + EMIS_COUNTS[states[j]])]
                            matrix[i][j][tuple(lst)] = np.prod(np.array(lst))
                    for key in matrix[i][j].keys():
                        if matrix[i][j][key] == max(matrix[i][j].values()):
                            break
                    matrix[i][j] = list(key)
        pos_tag = dict()
        pos_tag[tokens[-1]] = states[-1]
        for i in range(len(matrix[-2::-1])):
            pos_tag[tokens[-2::-1][i]] = states[matrix[-2::-1][i].index(matrix[-1][-1][:-2 * (i + 1)])]
        del pos_tag['^']
        del pos_tag['$']
        tokens.remove('^')
        tokens.remove('$')
        return pos_tag

    def search(self):
        normal_form_to_search = self.normal_form
        debug = []
        forms_count = 0
        for i in range(len(self.sentences)):
            matches = []
            normal_forms = {}
            sentence_tokenized = WordPunctTokenizer().tokenize(self.sentences[i].lower())
            sentence_tokenized.insert(0, '^')
            sentence_tokenized.append("$")
            primary_pos_tag = self.viterbi(sentence_tokenized, STATES)
            for token in sentence_tokenized:
                pos_tag_variant_probabilities = {}
                norm_forms = {}
                for k in range(len(MORPH_ANALYZER.parse(token))):
                    if MORPH_ANALYZER.parse(token)[k].tag.POS not in pos_tag_variant_probabilities.keys():
                        pos_tag_variant_probabilities[MORPH_ANALYZER.parse(token)[k].tag.POS] = \
                            MORPH_ANALYZER.parse(token)[
                                k].score
                    else:
                        pos_tag_variant_probabilities[MORPH_ANALYZER.parse(token)[k].tag.POS] += \
                            MORPH_ANALYZER.parse(token)[
                                k].score
                    if MORPH_ANALYZER.parse(token)[k].tag.POS not in norm_forms.keys():
                        norm_forms[MORPH_ANALYZER.parse(token)[k].tag.POS] = MORPH_ANALYZER.parse(token)[k].normal_form
                possible = set(pos_tag_variant_probabilities.keys()).intersection(
                    set(ANNOTATION_DECIPHER[primary_pos_tag[token]]))
                if len(possible) > 0:
                    for variant in possible:
                        if pos_tag_variant_probabilities[variant] == max(
                                [pos_tag_variant_probabilities[el] for el in possible]):
                            normal_forms[token] = norm_forms[variant]
                            break
                elif len(possible) == 0:
                    normal_forms[token] = MORPH_ANALYZER.parse(token)[0].normal_form
                reg = r"\b" + token + r"\b"
                if normal_forms[token] == normal_form_to_search:
                    matches += [(m.span()[0], m.span()[1]) for m in re.finditer(reg, self.sentences[i].lower())]
            matches = sorted(list(set(matches)), key=lambda to_mark: to_mark[0])
            if len(matches):
                forms_count += len(matches)
                highlighted_sentence = ''
                for j in range(len(matches)):
                    if j == 0:
                        highlighted_sentence += self.sentences[i][0:matches[0][0]] + \
                                                '<span style="background-color:yellow">' + \
                                                self.sentences[i][
                                                matches[0][0]:matches[0][1]] + \
                                                '</span>'
                    elif j == -1:
                        highlighted_sentence += self.sentences[i][
                                                matches[-2][1]:matches[-1][
                                                    0]] + \
                                                '<span style="background-color:yellow">' + \
                                                self.sentences[i][
                                                matches[-1][0]:matches[-1][
                                                    1]] + \
                                                '</span>'
                    else:
                        highlighted_sentence += self.sentences[i][
                                                matches[j - 1][1]:matches[j][
                                                    0]] + \
                                                '<span style="background-color:yellow">' + \
                                                self.sentences[i][
                                                matches[j][0]:matches[j][1]] + \
                                                '</span>'
                highlighted_sentence += self.sentences[i][matches[- 1][1]:len(self.sentences[i])]
                if self.debug_available:
                    debug.append((highlighted_sentence, False))
        self.extended_results['word_forms_count'] = {'value': forms_count,
                                                     'description': 'Количество употреблений форм слова',
                                                     'debug': debug}
        return forms_count

    def uniform_rows_count(self):
        """ IPM of sentences with uniform rows"""
        uniform_rows_count = 0
        converter = MorphRegexConverter(pos=('NOUN', 'ADJF', 'ADJS', 'VERB', 'INFN'))
        debug = []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences, self.sentences):
            converted_sentence, poses = converter.convert(sentence=parsed_sentence)
            raw_matches = list(UNIFORM_ROWS_REGEX.finditer(converted_sentence, overlapped=True))
            matches = []
            for match in raw_matches:
                match_start, match_end = None, None
                for pos in poses:
                    if pos.pos_start == match.start():
                        match_start = pos.start()
                    if pos.pos_end == match.end():
                        match_end = pos.end()
                if match_start and match_end:
                    matches.append(Match((match_start, match_end, ''), (match.start(), match.end(), '')))

                uniform_rows_count += len(matches)
                if self.debug_available and matches:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['uniform_rows_count'] = {'value': uniform_rows_count,
                                                       'description': 'Предложения с однородными рядами',
                                                       'debug': debug}
        return (uniform_rows_count / self.total_words) * IPM_MULTIPLIER

    def introductory_words_count(self):
        introductory_words_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(INTRO_WORDS_REGEXP.finditer(sentence, overlapped=True))
            if matches:
                introductory_words_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['introductory_words_count'] = {'value': introductory_words_count,
                                                             'description': 'Вводные слова и конструкции',
                                                             'debug': debug}
        return (introductory_words_count / self.total_words) * IPM_MULTIPLIER

    def comparatives_count(self):
        comparatives_count = 0
        converter = MorphRegexConverter(pos=('INFN',))
        debug = []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences, self.sentences):
            converted_sentence, poses = converter.convert(sentence=parsed_sentence)
            raw_pos_matches = list(COMPARATIVES_REGEX_POS.finditer(converted_sentence, overlapped=True))
            pos_matches = []
            for match in raw_pos_matches:
                pos = [pos for pos in poses if pos.pos_start == match.start(4) and pos.pos_end == match.end(4)][0]
                if 'с целью' in match.string.lower():
                    pos._start -= 8
                elif 'из расчeта' in match.string.lower() or 'из расчёта' in match.string.lower():
                    pos._start -= 11
                pos_matches.append(pos)
            matches = list(COMPARATIVES_REGEX.finditer(sentence))
            comparatives_count += len(pos_matches) + len(matches)
            if (pos_matches or matches) and self.debug_available:
                debug.append((highlight_match(sentence, matches + pos_matches), False))
        self.extended_results['comparatives_count'] = {'value': comparatives_count,
                                                       'description': 'Целевые и выделительные обороты',
                                                       'debug': debug}
        return (comparatives_count / self.total_words) * IPM_MULTIPLIER

    def comparatives_constructions_count(self):
        comparatives_constructions_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(COMPARATIVE_CONSTRUCTIONS_REGEX.finditer(sentence, overlapped=True))
            matches = [match for match in matches if match.groups()[2] != 'как'
                       or (' так и ' not in sentence and not any((w in match.string for w in (' как полагается',
                                                                            ' как правило',
                                                                            ' как это ни странно',
                                                                            ' как ни странно',
                                                                            ' как раз',
                                                                            ' как следует',
                                                                            ' как всегда',
                                                                            ' как никогда'))))]
            if matches:
                comparatives_constructions_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['comparatives_constructions_count'] = {'value': comparatives_constructions_count,
                                                                     'description': 'Конструкции с семантикой сравнения',
                                                                     'debug': debug}
        return (comparatives_constructions_count / self.total_words) * IPM_MULTIPLIER

    def syntax_splices_count(self):
        syntax_splices_count = 0
        debug = []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences, self.sentences):
            raw_pos_matches = SYNTAX_SPLICES_REGEX_POS.finditer(sentence, overlapped=True)
            pos_matches = []
            for raw_pos_match in raw_pos_matches:
                _, word1, _, word2, _ = raw_pos_match.groups()
                word1, word2 = parse_word_morph(word1), parse_word_morph(word2)
                if word1.tag.POS == 'VERB' and word2.tag.POS == 'VERB' \
                        and word1.word not in SYNTAX_SPLICES_EXCLUSIONS and word2.word not in SYNTAX_SPLICES_EXCLUSIONS:
                    pos_matches.append(raw_pos_match)

            matches = list(SYNTAX_SPLICES_REGEX.finditer(sentence, overlapped=True))
            if pos_matches or matches:
                syntax_splices_count += len(pos_matches) + len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, pos_matches + matches), False))
        self.extended_results['syntax_splices_count'] = {'value': syntax_splices_count,
                                                         'description': 'Синтаксические сращения',
                                                         'debug': debug}
        return (syntax_splices_count / self.total_words) * IPM_MULTIPLIER

    def comparative_clauses_count(self):
        comparative_clauses_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(COMPARATIVE_CLAUSES_REGEX.finditer(sentence, overlapped=True))
            if matches:
                comparative_clauses_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['comparative_clauses_count'] = {'value': comparative_clauses_count,
                                                              'description': 'Сравнительные придаточные',
                                                              'debug': debug}
        return (comparative_clauses_count / self.total_words) * IPM_MULTIPLIER

    def epenthetic_constructions_count(self):
        epenthetic_constructions_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(EPINTHETIC_CONSTRUCTIONS_REGEX.finditer(sentence, overlapped=True))
            matches = [match for match in matches if '»' not in sentence[match.start() - 2: match.start()]]
            if matches:
                epenthetic_constructions_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['epenthetic_constructions_count'] = {'value': epenthetic_constructions_count,
                                                                   'description': 'Вставные конструкции',
                                                                   'debug': debug}
        return (epenthetic_constructions_count / self.total_words) * IPM_MULTIPLIER

    def collation_clauses_count(self):
        collation_clauses_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(COLLATION_CLAUSES_REGEX.finditer(sentence, overlapped=True))
            if matches:
                collation_clauses_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['collation_clauses_count'] = {'value': collation_clauses_count,
                                                            'description': 'Конструкции с сопоставительными союзами',
                                                            'debug': debug}
        return (collation_clauses_count / self.total_words) * IPM_MULTIPLIER

    def complex_syntax_constructs_count(self):
        complex_syntax_constructs_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(COMPLEX_SYNTAX_REGEX.finditer(sentence, overlapped=True))
            if matches:
                complex_syntax_constructs_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['complex_syntax_constructs_count'] = {'value': complex_syntax_constructs_count,
                                                                    'description': 'Сложные синтаксические конструкции',
                                                                    'debug': debug}
        return (complex_syntax_constructs_count / self.total_words) * IPM_MULTIPLIER

    def single_verb_count(self):
        single_verb_count = 0
        debug = []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences_wo_punkt, self.sentences):
            is_single_verb = False
            for i, word in enumerate(parsed_sentence):
                for predicate_type in SINGLE_VERB_PREDICATES:
                    match = match_morph(word[1], SINGLE_VERB_PREDICATES[predicate_type])
                    if match:
                        predicate = (parsed_sentence[i - 1] if i > 0 else None, parsed_sentence[i])
                        subject_keys = ('first_case', 'second_case', 'third_case', 'fourth_case', 'fifth_case')
                        subject_rules = list(filter(lambda r: r[0] in subject_keys, SINGLE_VERB_SUBJECTS.items()))
                        has_subject = next((True for w in parsed_sentence
                                                for tags, b_words in subject_rules
                                                if match_morph(w[1], SINGLE_VERB_SUBJECTS[tags]) and (
                                                        not b_words[1] or (predicate[0] and predicate[0][1].normal_form in b_words[1]))),
                                               None)
                        if predicate_type == 'seventh_case' and not has_subject:
                            has_subject = next((True for word in parsed_sentence
                                                if match_morph(word[1], SINGLE_VERB_SUBJECTS['sixth_case'])
                                                and (not SINGLE_VERB_SUBJECTS['sixth_case'][1] or predicate[0][
                                1].normal_form in SINGLE_VERB_SUBJECTS['sixth_case'][1])),
                                               None)
                        if not has_subject:
                            single_verb_count += 1
                            is_single_verb = True
                            break
                if is_single_verb:
                    if self.debug_available:
                        debug.append((sentence, False))
                    break

        self.extended_results['single_verb_count'] = {'value': single_verb_count,
                                                      'description': 'Глагольные односоставные предложения',
                                                      'debug': debug}
        return (single_verb_count / self.total_words) * IPM_MULTIPLIER

    def appeal_count(self):
        appeal_count = 0
        converter = MorphRegexConverter(tags=('Name', 'Patr', 'Surn', 'NPRO', 'NOUN', 'ADJF', 'ADJF', 'Anum'))
        debug = []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences, self.sentences):
            converted_sentence, poses = converter.convert(sentence=parsed_sentence)
            raw_matches = list(APPEAL_REGEX.finditer(converted_sentence, overlapped=True))
            if len(list(filter(lambda s: s.group(1) and s.group(1).startswith(','), raw_matches))) > 1:
                raw_matches = list(filter(lambda s: not s.group(1).startswith(','), raw_matches))
            if raw_matches:
                matches = []
                for match in raw_matches:
                    match_start, match_end = None, None
                    start_ind, end_ind = 0, 0
                    for pos in poses:
                        if pos.pos_start == match.start(7):
                            start_ind = 7
                            match_start = pos.start()
                        elif pos.pos_start == match.start(3):
                            start_ind = 3
                            match_start = pos.start()
                        elif pos.pos_start == match.start(12):
                            start_ind = 12
                            match_start = pos.start()
                        elif pos.pos_start == match.start(20):
                            start_ind = 20
                            match_start = pos.start()
                        if pos.pos_end == match.end(7):
                            end_ind = 7
                            match_end = pos.end()
                        elif pos.pos_end == match.end(3):
                            end_ind = 3
                            match_end = pos.end()
                        elif pos.pos_end == match.end(12):
                            end_ind = 12
                            match_end = pos.end()
                        elif pos.pos_end == match.end(20):
                            end_ind = 20
                            match_end = pos.end()
                    if match_start is not None and match_end is not None:
                        matches.append(Match((match_start, match_end, ''), (match.start(start_ind), match.end(end_ind), '')))

                    appeal_count += len(matches)
                    if self.debug_available and matches:
                        debug.append((highlight_match(sentence, matches), False))
        self.extended_results['appeal_count'] = {'value': appeal_count,
                                                 'description': 'Обращения',
                                                 'debug': debug}
        return (appeal_count / self.total_words) * IPM_MULTIPLIER

    def dichotomy_pronouns_count(self):
        dichotomy_ours_count = 0
        dichotomy_theirs_count = 0
        ours_debug, theirs_debug = [], []
        for parsed_sentence, sentence in zip(self.morph_parsed_sentences, self.sentences):
            theirs_found, ours_found = False, False
            theirs_matches, ours_matches = [], []
            current_pos = 0
            for word in parsed_sentence:
                if not word[1]:
                    pass
                else:
                    try:
                        normal_form = parse_word_morph(word[1].methods_stack[0][1]).normal_form if len(word[1].methods_stack) > 1 else word[1].normal_form
                    except:
                        normal_form = word[1].normal_form
                    if normal_form in THEIRS_PRONOUNS:
                        theirs_found = True
                        dichotomy_theirs_count += 1
                        theirs_matches.append(Match((current_pos, current_pos + len(word[0]), '')))
                    elif normal_form in OURS_PRONOUNS:
                        ours_found = True
                        dichotomy_ours_count += 1
                        ours_matches.append(Match((current_pos, current_pos + len(word[0]), '')))
                current_pos += len(word[0])
            if ours_found and self.debug_available:
                ours_debug.append((highlight_match(sentence, ours_matches), False))
            if theirs_found and self.debug_available:
                theirs_debug.append((highlight_match(sentence, theirs_matches), False))
        self.extended_results['dichotomy_ours_count'] = {'value': dichotomy_ours_count,
                                                         'description': 'Местоимения "я, мы"-группы',
                                                         'debug': ours_debug}
        self.extended_results['dichotomy_theirs_count'] = {
            'value': dichotomy_theirs_count,
            'description': 'Местоимения "ты, вы"-группы',
            'debug': theirs_debug}
        return (dichotomy_ours_count / self.total_words) * IPM_MULTIPLIER, (
                dichotomy_theirs_count / self.total_words) * IPM_MULTIPLIER

    def complex_words_count(self):
        complex_words_count = 0
        debug = []
        for sentence in self.sentences:
            raw_matches = list(COMPLEX_WORDS_REGEX.finditer(sentence, overlapped=True))
            matches = []
            for raw_match in raw_matches:
                _, first_word, _, second_word, _ = raw_match.groups()
                parsed_first_word, parsed_second_word = parse_word_morph(first_word), parse_word_morph(second_word)
                if parsed_first_word.tag.POS != 'NOUN' \
                        or parsed_second_word.tag.POS != 'NOUN' \
                        or parsed_first_word.normal_form == parsed_second_word.normal_form \
                        or len(first_word) == 1 \
                        or len(second_word) == 1 \
                        or (first_word[0].isupper() and second_word[0].isupper()):
                    continue
                if parsed_first_word.tag.case == parsed_first_word.tag.case \
                        and parsed_first_word.tag.number == parsed_first_word.tag.number:
                    matches.append(raw_match)
            if matches:
                complex_words_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches, start_shift=0, end_shift=-1), False))
        self.extended_results['complex_words_count'] = {'value': complex_words_count,
                                                        'description': 'Сложные слова полуслитного написания',
                                                        'debug': debug}
        return (complex_words_count / self.total_words) * IPM_MULTIPLIER

    def modal_particles_count(self):
        modal_particles_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(MODAL_PARTICLES_REGEX.finditer(sentence, overlapped=True))
            if matches:
                modal_particles_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['modal_particles_count'] = {'value': modal_particles_count,
                                                          'description': 'Модальные частицы',
                                                          'debug': debug}
        return (modal_particles_count / self.total_words) * IPM_MULTIPLIER

    def modal_postfix_count(self):
        modal_postfix_count = 0
        debug = []
        for sentence in self.sentences:
            raw_matches = list(MODAL_POSTFIX_REGEX.finditer(sentence))
            if raw_matches:
                matches = list(filter(lambda x: parse_word_morph(
                    sentence[x.start():x.end()].strip()).normal_form not in MODAL_POSTFIX_EXCLUSIONS,
                                      raw_matches))
                modal_postfix_count += len(matches)
                if matches and self.debug_available:
                    debug.append((highlight_match(sentence, matches), False))
        self.extended_results['modal_postfix_count'] = {'value': modal_postfix_count,
                                                        'description': 'Наличие/отсутствие модального постфикса «-то»',
                                                        'debug': debug}
        return (modal_postfix_count / self.total_words) * IPM_MULTIPLIER

    def interjections_count(self):
        interjections_count = 0
        debug = []
        for sentence in self.sentences:
            matches = list(INTERJECTIONS_REGEXP.finditer(sentence, overlapped=True))
            if matches:
                interjections_count += len(matches)
                if self.debug_available:
                    debug.append((highlight_match(sentence, matches, end_shift=-1), False))
        self.extended_results['interjections_count'] = {'value': interjections_count,
                                                        'description': 'Междометия',
                                                        'debug': debug}
        return (interjections_count / self.total_words) * IPM_MULTIPLIER

    def intensifiers_count(self):
        intensifiers = {}
        debug = []
        for sentence in self.sentences:
            raw_matches = list(INTENSIFIERS_REGEX.finditer(sentence))
            for raw_match in raw_matches:
                substring = sentence[raw_match.start():raw_match.end()].lower()
                left_word, punkt1, main_word, punkt2, right_word = map(lambda s: s.lower() if s else s,
                                                                       raw_match.groups())
                left_word_pos, right_word_pos = parse_word_morph(left_word).tag.POS if left_word else None, \
                                                parse_word_morph(right_word).tag.POS if right_word else None
                # general rule for all words
                if left_word_pos in VERB_FORMS or right_word_pos in VERB_FORMS:
                    continue
                if 'действительно' in substring and ',' in substring:
                    continue
                if main_word in ('какой', 'какого', 'какому', 'каком', 'какое') \
                        and right_word_pos not in ('ADJF', 'ADJS', 'NOUN', 'ADVB', 'NPRO') \
                        and right_word not in ('уж', 'тут', 'здесь', 'такой', 'такая', 'такое'):
                    continue
                if any(word in main_word for word in ('настоящ', 'невероятн', 'чист', 'сущ')) \
                        and main_word != 'невероятно' \
                        and right_word_pos != 'NOUN':
                    continue
                if 'страшн' in main_word and main_word != 'страшно' and right_word_pos != 'NOUN':
                    continue
                if main_word == 'страшно' and right_word_pos not in ('ADJF', 'ADJS'):
                    continue
                if main_word == 'немного' and right_word_pos not in ('ADJF', 'ADJS'):
                    continue
                if main_word == 'так':
                    if punkt2 and ',' in punkt2:
                        continue
                    if right_word_pos not in ('ADJS', 'ADVB', 'PRTF', 'PRTS') \
                            and left_word_pos not in ('ADJS', 'ADVB'):
                        continue
                if 'так' in main_word and right_word_pos not in ('ADJF', 'ADJS', 'ADVB', 'NPRO'):
                    continue
                if main_word == 'чуть' and right_word not in ('ли', 'не') and right_word_pos not in ('ADJF', 'ADJS'):
                    continue

                if intensifiers.get(main_word):
                    intensifiers[main_word] += 1
                else:
                    intensifiers[main_word] = 1
                if self.debug_available:
                    debug.append((highlight_match(sentence, [raw_match], 3), False, main_word))
        intensifiers_score = {}
        for word in intensifiers:
            ll_score = log_likelihood(word, intensifiers[word], self.total_words)
            intensifiers_score[word] = ll_score
        self.extended_results['intensifiers_count'] = {'value': sum(intensifiers.values()),
                                                       'description': 'Предпочтительные слова-интенсификаторы',
                                                       'debug': debug}
        return intensifiers_score

    def keywords_count(self):
        words_freq = nltk.FreqDist(
            (word[1].normal_form for sent in self.morph_parsed_sentences_wo_punkt for word in sent))
        keywords = {}
        for word in words_freq:
            ll_score = log_likelihood(word, words_freq[word], self.total_words)
            if ll_score >= 50:
                keywords[word] = ll_score
        self.extended_results['keywords_count'] = {'value': len(keywords),
                                                   'description': 'Ключевые слова',
                                                   'debug': list(map(lambda x: (f'{x[0]} - {x[1]}', False, x[1]),
                                                                     keywords.items())) if self.debug_available else []}
        return keywords

    def bigrams_count(self):
        bigrams = create_bigrams(self.morph_parsed_sentences_wo_punkt)
        bigrams = {f'{bigram[0]} {bigram[1]}': round((value / self.total_words) * IPM_MULTIPLIER, 4) for
                   bigram, value in bigrams}
        self.extended_results['bigrams_count'] = {'value': len(bigrams),
                                                  'description': 'Наиболее частотные биграммы',
                                                  'debug': list(map(lambda x: (f'{x[0]} - {x[1]}', False, x[1]),
                                                                    bigrams.items())) if self.debug_available else []}
        return bigrams

    def trigrams_count(self):
        trigrams = create_trigrams(self.morph_parsed_sentences_wo_punkt)
        trigrams = {
            f'{trigram[0]} {trigram[1]} {trigram[2]}': round((value / self.total_words) * IPM_MULTIPLIER, 4)
            for trigram, value
            in trigrams}
        self.extended_results['trigrams_count'] = {'value': len(trigrams),
                                                   'description': 'Наиболее частотные триграммы',
                                                   'debug': list(map(lambda x: (f'{x[0]} - {x[1]}', False, x[1]),
                                                                     trigrams.items())) if self.debug_available else []}
        return trigrams

    def standalone_constructions_count(self):
        standalone_constructions_count = 0
        debug = []
        for sentence in self.sentences:
            raw_matches = list(STANDALONE_CONSTRUCTIONS_REGEX.finditer(sentence))
            matches = []
            for match in raw_matches:
                first_part, second_part = match.groupdict().values()
                first_part, second_part = parse_sentence_morph(first_part), parse_sentence_morph(second_part)
                first_part_nouns = [(w[1].tag.case, w[1].tag.number) for w in first_part if
                                    w[1] and w[1].tag.POS == 'NOUN']
                if not first_part_nouns:
                    continue
                second_part_nouns = [(w[1].tag.case, w[1].tag.number) for w in second_part if
                                     w[1] and w[1].tag.POS == 'NOUN']
                if set(second_part_nouns) & set(first_part_nouns):
                    standalone_constructions_count += 1
                    matches.append(match)
            if self.debug_available and matches:
                debug.append((highlight_match(sentence, matches), False))
        self.extended_results['standalone_constructions_count'] = {'value': standalone_constructions_count,
                                                                   'description': 'Предложения с обособленными приложениями',
                                                                   'debug': debug}
        return (standalone_constructions_count / self.total_words) * IPM_MULTIPLIER

    def calculate_results(self):
        if 'flesch_kincaid_index' in self.attributes.keys():
            self.results['flesch_kincaid_index'] = {'name': self.attributes['flesch_kincaid_index']['name'],
                                                    'result': self.flesch_kincaid_index()}
        if 'fog_index' in self.attributes.keys():
            self.results['fog_index'] = {'name': self.attributes['fog_index']['name'],
                                         'result': self.fog_index()}
        if 'avg_word_len' in self.attributes.keys():
            self.results['avg_word_len'] = {'name': self.attributes['avg_word_len']['name'],
                                            'result': self.avg_word_len()}
        if 'avg_sentence_len' in self.attributes.keys():
            self.results['avg_sentence_len'] = {'name': self.attributes['avg_sentence_len']['name'],
                                                'result': self.avg_sent_len_in_words()}
        if 'sentence_len8_count' in self.attributes.keys():
            self.results['sentence_len8_count'] = {'name': self.attributes['sentence_len8_count']['name'],
                                                   'result': self.sentence_len8_count()}
        if 'pr_coefficient' in self.attributes.keys():
            self.results['pr_coefficient'] = {'name': self.attributes['pr_coefficient']['name'],
                                              'result': self.pr_coefficient()}
        if 'qu_coefficient' in self.attributes.keys():
            self.results['qu_coefficient'] = {'name': self.attributes['qu_coefficient']['name'],
                                              'result': self.qu_coefficient()}
        if 'ac_coefficient' in self.attributes.keys():
            self.results['ac_coefficient'] = {'name': self.attributes['ac_coefficient']['name'],
                                              'result': self.ac_coefficient()}
        if 'din_coefficient' in self.attributes.keys():
            self.results['din_coefficient'] = {'name': self.attributes['din_coefficient']['name'],
                                               'result': self.din_coefficient()}
        if 'con_coefficient' in self.attributes.keys():
            self.results['con_coefficient'] = {'name': self.attributes['con_coefficient']['name'],
                                               'result': self.con_coefficient()}
        if 'errors' in self.attributes.keys():
            self.results['errors'] = {'name': self.attributes['errors']['name'],
                                      'result': self.get_errors()}
        if 'uniform_rows_count' in self.attributes.keys():
            self.results['uniform_rows_count'] = {'name': self.attributes['uniform_rows_count']['name'],
                                                  'result': self.uniform_rows_count()}
        if 'standalone_constructions_count' in self.attributes.keys():
            self.results['standalone_constructions_count'] = {
                'name': self.attributes['standalone_constructions_count']['name'],
                'result': self.standalone_constructions_count()}
        if 'introductory_words_count' in self.attributes.keys():
            self.results['introductory_words_count'] = {'name': self.attributes['introductory_words_count']['name'],
                                                        'result': self.introductory_words_count()}
        if 'word_forms_count' in self.attributes.keys():
            self.results['word_forms_count'] = {'name': self.attributes['word_forms_count']['name'],
                                                'result': self.search()}
        if 'comparatives_count' in self.attributes.keys():
            self.results['comparatives_count'] = {'name': self.attributes['comparatives_count']['name'],
                                                  'result': self.comparatives_count()}
        if 'comparatives_constructions_count' in self.attributes.keys():
            self.results['comparatives_constructions_count'] = {
                'name': self.attributes['comparatives_constructions_count']['name'],
                'result': self.comparatives_constructions_count()}
        if 'syntax_splices_count' in self.attributes.keys():
            self.results['syntax_splices_count'] = {'name': self.attributes['syntax_splices_count']['name'],
                                                    'result': self.syntax_splices_count()}
        if 'comparative_clauses_count' in self.attributes.keys():
            self.results['comparative_clauses_count'] = {'name': self.attributes['comparative_clauses_count']['name'],
                                                         'result': self.comparative_clauses_count()}
        if 'collation_clauses_count' in self.attributes.keys():
            self.results['collation_clauses_count'] = {
                'name': self.attributes['collation_clauses_count']['name'],
                'result': self.collation_clauses_count()}
        if 'epenthetic_constructions_count' in self.attributes.keys():
            self.results['epenthetic_constructions_count'] = {
                'name': self.attributes['epenthetic_constructions_count']['name'],
                'result': self.epenthetic_constructions_count()}
        if 'complex_syntax_constructs_count' in self.attributes.keys():
            self.results['complex_syntax_constructs_count'] = {
                'name': self.attributes['complex_syntax_constructs_count']['name'],
                'result': self.complex_syntax_constructs_count()}
        if 'single_verb_count' in self.attributes.keys():
            self.results['single_verb_count'] = {
                'name': self.attributes['single_verb_count']['name'],
                'result': self.single_verb_count()}
        if 'appeal_count' in self.attributes.keys():
            self.results['appeal_count'] = {
                'name': self.attributes['appeal_count']['name'],
                'result': self.appeal_count()}
        if 'dichotomy_pronouns_count' in self.attributes.keys():
            dichotomy_ours_count, dichotomy_theirs_count = self.dichotomy_pronouns_count()
            self.results['dichotomy_ours_count'] = {
                'name': 'Местоимения "я, мы"-группы',
                'result': dichotomy_ours_count}
            self.results['dichotomy_theirs_count'] = {
                'name': 'Местоимения "ты, вы"-группы',
                'result': dichotomy_theirs_count}
        if 'complex_words_count' in self.attributes.keys():
            self.results['complex_words_count'] = {
                'name': self.attributes['complex_words_count']['name'],
                'result': self.complex_words_count()}
        if 'modal_particles_count' in self.attributes.keys():
            self.results['modal_particles_count'] = {
                'name': self.attributes['modal_particles_count']['name'],
                'result': self.modal_particles_count()}
        if 'interjections_count' in self.attributes.keys():
            self.results['interjections_count'] = {
                'name': self.attributes['interjections_count']['name'],
                'result': self.interjections_count()}
        if 'modal_postfix_count' in self.attributes.keys():
            self.results['modal_postfix_count'] = {
                'name': self.attributes['modal_postfix_count']['name'],
                'result': self.modal_postfix_count()}

        # correlation-based parameters
        keywords = self.keywords_count() if 'keywords_count' in self.attributes.keys() else {}
        bigrams = self.bigrams_count() if 'bigrams_count' in self.attributes.keys() else {}
        trigrams = self.trigrams_count() if 'trigrams_count' in self.attributes.keys() else {}
        intensifiers = self.intensifiers_count() if 'intensifiers_count' in self.attributes.keys() else {}

        return self.results, self.extended_results, keywords, bigrams, trigrams, intensifiers

