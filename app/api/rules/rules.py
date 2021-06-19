import regex as re

UNIFORM_ROWS = (
    r'(NOUN,\s*NOUN,\s*NOUN)',
    r'(ADJF,\s*ADJF,\s*ADJF)',
    r'(ADJS,\s*ADJS,\s*ADJS)',
    r'(VERB,\s*VERB,\s*VERB)',
    r'(INFN,\s*INFN,\s*INFN)',
    r'((и|да и|ни|или|либо) NOUN,\s*(и|да и|ни|или|либо) NOUN,\s*(и|да и|ни|или|либо) NOUN)',
    r'(NOUN,\s*NOUN (да|и|либо|или|да и) NOUN)',
    r'(NOUN,\s*(да|и|да и|также|тоже|также и|либо|или) NOUN,\s*(да|и|да и|также|тоже|также и|либо|или) NOUN)',
    r'(NOUN,\s*(а|но) NOUN,\s*NOUN)',
    r'(NOUN,\s*NOUN,\s*(а|но) NOUN)',
    r'(NOUN и NOUN,\s*(а|но) NOUN)',
)

SENTENCES_SPLIT_LIST = (
    r'([^,]\n+\s+\n+)',
    r'(\n+([А-Я]{1}))'
)

ADDITIONAL_ABBREVIATIONS = (
    'оф',
    'производствен',
    *set(map(str, range(0, 100))),
)

COLLATION_ROWS = (
    r'((^|\s|,)если .+,\s*то .+?(;|$))',
    r'((^|\s|,)как,\s*так и .+?(;|$))',
    r'((^|\s|,)не только,\s*и .+?(;|$))',
    r'((^|\s|,)не только,\s*но и .+?(;|$))',
    r'((^|\s|,)не столько,\s*сколько .+?(;|$))',
    r'(,\s*в то время как .+?(;|$))',
    r'(^в то время как .+,.+?(;|$))',
    r'(,\s*тогда как .+?(;|$))',
    r'(^тогда как .+,.+?(;|$))',
    r'(^между тем как .+,.+?(;|$))',
    r'(,\s*между тем как .+?(;|$))',
    r'(^ровно как .+,.+?(;|$))',
    r'(,\s*ровно как .+?(;|$))',
    r'(^так же как .+,.+?(;|$))',
    r'(,\s*так же как .+?(;|$))',
    r'((^|\s|,)хотя и .+,\s*но .+?(;|$))',
    r'((^|\s|,)не то чтобы .+,\s*но .+?(;|$))',
    r'((^|\s|,)поскольку .+,\s*постольку .+?(;|$))',
    r'((\s|,|:)постольку,\s*постольку .+?(;|$))',
)

COMPLEX_SYNTAX_ROWS = (
    r'(,\s*(и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и .+,\s*который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то, что|невзирая на то, что|правда,|так что|чем|нежели) \w+)',
    r'(,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя/хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели \w+,\s*(и|а|но|да)|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и) \w+)',
    r'(,\s*(и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и) .+:)',
    r'(:\s*\S+,\s*(а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и) \w+)',
    r'(,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели)\s*:\s*\w+)',
    r'(:\s*.+,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели)\s*\w+)',
    r'(,\s*(и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и .+,\s*который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели) .+:\s*\w+)',
    r'(,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели .+,\s*и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и)\s*:\s*\w+)',
    r'(:\s*.+,\s*.+,\s*(и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и .+,\s*который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели) \w+)',
    r'(:\s*.+,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели .+,\s*(и|а|но|да)|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и)\s*:\s*\w+)',
    r'(,\s*(и|а|но|да|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и .+:\s*.+,\s*(который|чей|что|какой|где|куда|откуда)|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели) \w*)',
    r'(,\s*(который|чей|что|какой|где|куда|откуда|когда|что|чтобы|будто|будто бы|как|словно|ли|кто|что|который|какой|чтобы|как будто|будто|словно|насколько|пока|пока не|как|как только|лишь только|едва только|стоило как|не прошло как|если|если бы|когда|кабы|как раз|скоро|ежели|если бы|когда бы|коли|коль|для того чтобы|с той целью чтобы|дабы|только бы|лишь бы|потому что|оттого что|благодаря тому что|так как|из-за того что|ибо|благодаря тому что|в виду того что|тем более что|хотя|хоть|пусть|пускай|даром что|несмотря на то,\s*что|невзирая на то,\s*что|правда,|так что|чем|нежели .+:\s*(и|а|но|да)|тоже|также|ни|зато|однако|то ли|или|только|не то|да и|но и) \w+)',
)

MODAL_POSTFIX_EXCLUSIONS = (
    'кто-то',
    'что-то',
    'когда-то',
    'какой-то',
    'чей-то',
    'сколько-то',
    'как-то',
    'каков-то',
    'чего-то',
    'чем-то',
    'чём-то',
    'где-то',
    'куда-то',
    'откуда-то',
    'почему-то',
    'зачем-то',
    'то-то'
)

SYNTAX_SPLICES_EXCLUSIONS = ('нет', 'нет-нет', 'нетнет')

VERB_FORMS = ('VERB', 'INFN', 'PRTF', 'PRTS', 'GRND')

UNIFORM_ROWS_REGEX = re.compile('|'.join(UNIFORM_ROWS), flags=re.IGNORECASE)

COMPARATIVES_REGEX_POS = re.compile('(^|[\\s,:\-—«»"\'])(с целью|из расч(е|ё)та) (INFN)($|[\\s,.:\-—«»"\'])',
                                    flags=re.IGNORECASE)
COMPARATIVES_REGEX = re.compile('(^|[\\s,:\-—«»"\'])(кроме|помимо|включая|наряду с)([\\s,:«»"\'])',
                                flags=re.IGNORECASE)
COMPARATIVE_CONSTRUCTIONS_REGEX = re.compile('((,\\s*)(как|будто|словно|точно|как будто) (\w+)*.*(\.|$))|(^(как|будто|словно|точно|как будто) .*,\\s*.*\.$)', flags=re.IGNORECASE)

SYNTAX_SPLICES_REGEX_POS = re.compile('(^|[\\s,:—«»"\'])([а-яА-Яё\-]+)\s+(да и|да)\s+([а-яА-Яё\-]+)($|[\\s,.:—«»"\'])',
                                      flags=re.IGNORECASE)
SYNTAX_SPLICES_REGEX = re.compile(
    r'(^|[\s,:\-—«»"\'])(что было,\s*то было|что было,\s*то и есть|что было,\s*то есть|что есть,\s*то есть|что есть,\s*то и есть|что есть,\s*то и будет|что есть,\s*то будет)($|[\s,.:\-—«»"\'])',
    flags=re.IGNORECASE)

COMPARATIVE_CLAUSES_REGEX = re.compile(
    r'(\b(как|подобно тому как|ровно тому как) .+,\s*\b)|(,\s*как .+,\s*\b)|(\b(подобно тому|ровно тому,\s*как) \b)|(\b(как будто|будто|словно|точно) .+,\s*\b)|(, (как будто|будто|словно|точно) \b)',
    flags=re.IGNORECASE)

EPINTHETIC_CONSTRUCTIONS_REGEX = re.compile(r'(\s+(-|—|—)\s+.+\s+(-|—|—)\s+)|(\(.+\))', flags=re.IGNORECASE)

COLLATION_CLAUSES_REGEX = re.compile("|".join(COLLATION_ROWS), flags=re.IGNORECASE)

COMPLEX_SYNTAX_REGEX = re.compile('|'.join(COMPLEX_SYNTAX_ROWS), flags=re.IGNORECASE)

APPEAL_REGEX = re.compile('((^|,\s)(Name|Patr|Surn)(,\s|!|\.|$))|((^|,\s)(Name (Patr|Surn))(,\s|!|\.|$))|((^|,\s)(Name Patr Surn)(,\s|!|\.|$))|((^|,\s)(Surn Name)(,\s|!|\.|$))|((^|\s)эй,\s*(NPRO|NOUN|ADJF|ADJF|Anum)(,|!|$))', flags=re.IGNORECASE)

OURS_PRONOUNS, THEIRS_PRONOUNS = ('я', 'мы', 'мой', 'наш'), \
                                 ('он', 'вы', 'ты', 'она', 'они', 'её', 'ee', 'его', 'их', 'ваш', 'твой')
PRONOUNS_EXCLUSIONS = ('кто', 'что', 'чей', 'какой', 'как', 'каков', 'чего', 'чем', 'где', 'куда', 'откуда')

COMPLEX_WORDS_REGEX = re.compile(r'(^|\s|,|—|:|«|»|"|\')([А-ЯЁa-яё]+)(-|—)([а-яё]+)($|\s|,|\.|:|—|«|»|"|\')',
                                 flags=re.IGNORECASE)

MODAL_POSTFIX_REGEX = re.compile(r'(\s+|^)[a-яё]+(\-|\—)то(\s+|!|\?|\.|$)')

SENTENCES_SPLIT_REGEX = re.compile(r'\n+\s*\n+', flags=re.IGNORECASE)
SENTENCES_SPLIT_ADD_REGEX = re.compile(r'(\n+)([А-ЯЁ]{1})([^А-ЯЁ]{1})')

STANDALONE_CONSTRUCTIONS_REGEX = re.compile(
    r'(\b(?P<first>[a-яё]+)((\s+(-|—|–)\s+)(?P<second>.+(-|—|–)\s+))|(\b(?P<first>[a-яё]+)(,\s*(то есть|или|как)\s+))(?P<second>.+))', flags=re.IGNORECASE)

SINGLE_VERB_PREDICATES = {'first_case': ({'pos': ('VERB',),
                                          'mood': ('indc',),
                                          'tense': ('pres', 'futr'),
                                          'numbers': ('plur', 'sing'),
                                          'person': ('1per', '2per'),
                                          }, None),
                          'second_case': ({'pos': ('VERB',),
                                           'mood': ('impr',),
                                           'number': ('plur', 'sing'), }, None),
                          'third_case': ({'pos': ('VERB',),
                                          'person': ('3per',),
                                          'number': ('plur', 'sing'),
                                          'mood': ('indc',),
                                          'tense': ('pres', 'futr'),
                                          }, None),
                          'fourth_case': ({'pos': ('VERB',),
                                           'tense': ('past',),
                                           'number': ('sing',),
                                           'gender': ('neut',)
                                           }, None),
                          'fifth_case': ({'pos': ('VERB',),
                                          'person': ('3per',),
                                          'number': ('sing',),
                                          'tense': ('pres',),
                                          }, None),
                          'sixth_case': ({
                                             'pos': ('PRTS',),
                                             'gender': ('neut',),
                                             'voice': ('pssv',)
                                         }, None),
                          'seventh_case': ({
                                               'pos': ('INFN',),
                                           }, None)
                          }

SINGLE_VERB_SUBJECTS = {'first_case': ({'pos': ('NOUN', 'NPRO'),
                                        'number': ('plur', 'sing'),
                                        'case': ('nomn',)
                                        }, None),
                        'second_case': ({
                                            'pos': ('NOUN',),
                                            'number': ('plur', 'sing'),
                                            'case': ('nomn',)
                                        }, None),
                        'third_case': ({
                                           'pos': ('NOUN',),
                                           'number': ('plur', 'sing'),
                                           'case': ('gen1', 'gen2')
                                       }, ('много', 'мало', 'несколько')),
                        'fourth_case': ({'pos': ('NOUN', 'NPRO'),
                                         'number': ('plur', 'sing'),
                                         'case': ('gen1', 'gen2')
                                         }, 'у'),
                        'fifth_case': ({'pos': ('NOUN', 'NPRO'),
                                        'number': ('plur', 'sing'),
                                        'case': ('datv',)
                                        }, None),
                        'sixth_case': ({
                                           'pos': ('VERB',),
                                           'number': ('plur', 'sing'),
                                           'tense': ('pres', 'futr', 'past'),
                                       }, None)
                        }
