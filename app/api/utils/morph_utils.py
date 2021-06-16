import itertools
import re

import nltk
import pymorphy2
from nltk.data import load
from nltk.tokenize import word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktLanguageVars

from app.api.rules.rules import SENTENCES_SPLIT_REGEX, ADDITIONAL_ABBREVIATIONS, SENTENCES_SPLIT_ADD_REGEX

PUNCTUATION = ' "#$%&()*+.!?«»,\'-/:;<=>@[]^_`{|}~—…'
MORPH_ANALYZER = pymorphy2.MorphAnalyzer()
TAG = MORPH_ANALYZER.TagClass

nltk.download('punkt')

TOKENIZER = load("tokenizers/punkt/{0}.pickle".format('russian'))
TOKENIZER._params.abbrev_types.update(ADDITIONAL_ABBREVIATIONS)


def tokenize_sentences(text):
    result = []
    sentences = text.split('…\n')
    for sentence in sentences:
        result.extend(TOKENIZER.tokenize(sentence))
    return [s.replace('\r\n', '\n').replace('\n\n', '\n').strip() for s in result]


def tokenize_corp_sentences(text):
    raw_sentences = TOKENIZER.tokenize(text)
    sentences = []
    for raw_sentence in raw_sentences:
        new_sentences = SENTENCES_SPLIT_REGEX.split(raw_sentence)
        skip_next = False
        for ind, new_sentence in enumerate(new_sentences):
            new_sentence = new_sentence.replace('\n\n', '\n')
            #sentences = new_sentence.split()
            # matches = list(SENTENCES_SPLIT_ADD_REGEX.finditer(new_sentence))
            # if matches:
            #     current_pos = 0
            #     for ind, match in enumerate(matches):
            #         if ind == 0:
            #             sentences.append(new_sentence[:match.start()])
            #             current_pos = match.end() - len(match.groups())
            #         else:
            #             sentences.append(new_sentence[current_pos:match.start()])
            #             current_pos = match.end() - len(match.groups())
            #     sentences.append(new_sentence[current_pos:])
            # else:
            #     sentences.append(new_sentence)
            if skip_next:
                continue
            if new_sentence[-1] in (',',) and ind < len(new_sentences) - 1:
                sentences.append(' '.join((new_sentence, new_sentences[ind + 1])))
                skip_next = True
            elif ind < len(new_sentences) - 1 and new_sentences[ind + 1][0].islower() and new_sentence[-1] not in ',.?!':
                sentences.append(' '.join((new_sentence, new_sentences[ind + 1])))
                skip_next = True
            else:
                new_sentence = new_sentence.replace('\n', ' ')
                sentences.append(new_sentence)
    return sentences


def parse_word_morph(word):
    return MORPH_ANALYZER.parse(word)[0]


def parse_sentence_morph(sentence):
    parsed_sentence = []
    sentence = sentence.replace('  ', ' ')
    ll = [[word_tokenize(w), ' '] for w in re.split('\\s|"', sentence)]
    for word in list(itertools.chain(*list(itertools.chain(*ll)))):
        if word in PUNCTUATION:
            parsed_sentence.append((word, None))
        else:
            parsed_sentence.append((word, parse_word_morph(word)))
    return parsed_sentence[:-1]


class Match:
    def __init__(self, word, pos=('', '', '')):
        self._start, self._end, self.word = word[0], word[1], word[2]
        self.pos_start, self.pos_end, self.pos_word = pos[0], pos[1], pos[2]

    def start(self):
        return self._start

    def end(self):
        return self._end


class MorphRegexConverter:
    def __init__(self, pos=None, tags=None):
        self.pos = pos
        self.tags = tags

    def convert(self, sentence):
        converted_sentence = ''
        all_poses, current_pos, converted_pos = [], 0, 0
        for word, parsed_word in sentence:
            if not parsed_word:
                converted_sentence += word
                converted_pos += len(word)
                current_pos += len(word)
            else:
                if self.pos and parsed_word.tag.POS in self.pos:
                    converted_sentence += parsed_word.tag.POS
                    all_poses.append(Match((current_pos, current_pos + len(word), word),
                                           (converted_pos, converted_pos + len(parsed_word.tag.POS), parsed_word.tag.POS)))
                    current_pos += len(word)
                    converted_pos += len(parsed_word.tag.POS)
                else:
                    if self.tags:
                        found = False
                        for tag in self.tags:
                            if tag in parsed_word.tag:
                                found = True
                                converted_sentence += tag
                                all_poses.append(Match((current_pos, current_pos + len(word), word),
                                                       (converted_pos, converted_pos + len(tag), tag)))
                                converted_pos += len(tag)
                                current_pos += len(word)
                                break
                        if not found:
                            converted_sentence += word
                            converted_pos += len(word)
                            current_pos += len(word)
                    else:
                        converted_sentence += word
                        converted_pos += len(word)
                        current_pos += len(word)
        return converted_sentence, all_poses


class ExtendedMorphRegexConverter:
    """
    pattern = {'pos': ('Noun',),
               'genus': ('m', 'f'),
               'rename_to': 'NOUN',
               'anim': ('anim',),
               'number': ('sing', 'plur'),
               'case': ('nom','gen'),
               'person': ('1p', '2p'),
               }
    """
    def __init__(self, patterns: list):
        self.patterns = patterns

    def convert(self, sentence):
        converted_sentence = ''
        for word, parsed_word in sentence:
            if not parsed_word:
                converted_sentence += word
            else:
                for pattern in self.patterns:
                    if pattern.get('pos') and parsed_word.tag.POS not in pattern['pos']:
                        converted_sentence += word
                        continue
                    if pattern.get('person') and parsed_word.tag.person not in pattern['person']:
                        converted_sentence += word
                        continue
                    if pattern.get('number') and parsed_word.tag.number not in pattern['number']:
                        converted_sentence += word
                        continue
                    converted_sentence += pattern['rename_to']
        return converted_sentence


def match_tags(sentence, tags):
    matches = 0
    for word, parsed_word in sentence:
        if not parsed_word:
            continue
        else:
            for tag in tags:
                if set(tag) in parsed_word.tag:
                    matches += 1
    return matches


def match_morph(word, tags):
    try:
        for tag in tags[0]:
            if not any((t in word.tag for t in tags[0][tag])):
                return False
        return True
    except Exception as e:
        pass
