<template>
    <div class="content">
        <template v-if="selected !== null">
            <md-dialog :md-active.sync="showDialog" md-click-outside-to-close>
                <md-dialog-title>
                    <div class="md-layout md-gutter md-alignment-center-center">
                        <div class="md-layout-item">
                            {{ selected.description}}
                        </div>
                        <div class="md-layout md-alignment-center-right">
                            <md-button class="md-primary md-layout-item md-size-15" @click="showDialog = false">
                                <md-icon>close</md-icon>
                            </md-button>
                        </div>
                    </div>
                </md-dialog-title>
                <md-dialog-content>
                    <md-tabs>
                        <md-tab id="text1" md-label="Текст 1" class="md-scrollbar">
                            <md-table v-model="selected.first_text.debug" md-card>
                                <md-table-row slot="md-table-row" slot-scope="{ item }">
                                    <md-table-cell md-label="Пример" md-sort-by="item"><p v-html="item[0]">{{ item[0]
                                        }}</p></md-table-cell>
                                    <md-table-cell md-label="Исключить">
                                        <md-checkbox v-model="item[1]"></md-checkbox>
                                    </md-table-cell>
                                </md-table-row>
                            </md-table>
                        </md-tab>
                        <md-tab id="text2" md-label="Текст 2" class="md-scrollbar">
                            <md-table v-model="selected.second_text.debug" md-card>
                                <md-table-row slot="md-table-row" slot-scope="{ item }">
                                    <md-table-cell md-label="Пример" md-sort-by="item"><p v-html="item[0]">{{ item[0]
                                        }}</p></md-table-cell>
                                    <md-table-cell md-label="Исключить">
                                        <md-checkbox v-model="item[1]"></md-checkbox>
                                    </md-table-cell>
                                </md-table-row>
                            </md-table>
                        </md-tab>
                    </md-tabs>
                </md-dialog-content>
            </md-dialog>
        </template>
        <md-toolbar md-elevation="0">
            <div>
                <h4 style="text-align: left;">Настоящий ресурс предназначен для решения идентификационных задач
                    атрибуции
                    письменных текстов.
                </h4>
                <h4 style="text-align: left">Для того чтобы начать работу, выберите два текста, которые хотите
                    сравнить на предмет авторства,
                    скопируйте их в соответствующие поля, выберите набор метрик, которые необходимо посчитать для
                    конечных математических моделей текстов, интерпретируйте результаты полученных коэффициентов
                    сравнения математических моделей двух сравниваемых текстов.</h4>
            </div>
        </md-toolbar>

        <md-steppers :md-active-step.sync="active" md-linear>
            <md-step id="first_step" md-label="Первый текст" md-description="Обязательный шаг"
                     :md-done.sync="first_step">
                <div class="md-layout md-gutter md-alignment-center-center">
                    <div class="md-layout-item">
                        <md-field id="firstTextGenre">
                            <label for="firstTextGenre">Жанр</label>
                            <md-select v-model="first_text_genre" name="firstTextGenre">
                                <md-option v-for="genre in genres" v-bind:value="genre.value" :key="genre.value">{{
                                    genre.text }}
                                </md-option>
                            </md-select>
                        </md-field>

                    </div>
                </div>
                <div class="md-layout md-gutter md-alignment-center-center">
                    <div class="md-layout-item">
                        <md-field>
                            <label>Загрузите первый текст</label>
                            <md-file @change="loadFirstTextFromFile"/>
                        </md-field>
                    </div>
                    <div class="md-layout-item">
                        <md-field  >
                            <label>Кодировка</label>
                            <md-select v-model="first_text_encoding" @md-selected="changeFirstTextEncoding">
                                <md-option value="CP1251">Windows-1251</md-option>
                                <md-option value="utf-8">UTF-8</md-option>
                                <md-option value="UTF-16">UTF-16</md-option>
                                <md-option value="KOI8-R">KOI8-R</md-option>
                            </md-select>
                        </md-field>
                    </div>
                </div>
                <md-field md-clearable>
                    <label>Введите первый текст</label>
                    <md-textarea v-model="first_text"></md-textarea>
                </md-field>
                <md-button class="md-raised md-primary" :disabled="!first_text"
                           @click="setDone('first_step', 'second_step')">Продолжить
                </md-button>
            </md-step>

            <md-step id="second_step" md-label="Второй текст" md-description="Обязательный шаг"
                     :md-done.sync="second_step">
                <div class="md-layout md-gutter md-alignment-center-center">
                    <div class="md-layout-item">
                        <md-field id="secondTextGenre">
                            <label for="secondTextGenre">Жанр</label>
                            <md-select v-model="second_text_genre" name="secondTextGenre">
                                <md-option v-for="genre in genres" v-bind:value="genre.value" :key="genre.value">{{
                                    genre.text }}
                                </md-option>
                            </md-select>
                        </md-field>
                    </div>
                </div>
                <div class="md-layout md-gutter md-alignment-center-center">
                    <div class="md-layout-item">
                        <md-field>
                            <label>Загрузите второй текст</label>
                            <md-file @change="loadSecondTextFromFile"/>
                        </md-field>
                    </div>
                    <div class="md-layout-item">
                        <md-field>
                            <label>Кодировка</label>
                            <md-select v-model="second_text_encoding" @md-selected="changeSecondTextEncoding">
                                <md-option value="CP1251">Windows-1251</md-option>
                                <md-option value="UTF-8">UTF-8</md-option>
                                <md-option value="UTF-16">UTF-16</md-option>
                                <md-option value="KOI8-R">KOI8-R</md-option>
                            </md-select>
                        </md-field>
                    </div>
                </div>
                <md-field md-clearable>
                    <label>Введите второй текст</label>
                    <md-textarea v-model="second_text"></md-textarea>
                </md-field>
                <md-button class="md-raised md-primary" :disabled="!second_text"
                           @click="setDone('second_step', 'third_step')">Продолжить
                </md-button>
            </md-step>

            <md-step id="third_step" class="md-layout md-gutter md-alignment-center" md-label="Выбор атрибутов"
                     md-description="Опциональный шаг"
                     :md-done.sync="third_step">
                <div class="md-layout md-gutter" style="justify-content:center">
                    <div class="viewport">
                        <md-list>
                            <md-subheader>Стилостатистика</md-subheader>
                            <md-list-item :key="attributes.flesch_kincaid_index.name">
                                <md-checkbox v-model="attributes.flesch_kincaid_index.checked"/>
                                <span class="md-list-item-text">{{ attributes.flesch_kincaid_index.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.fog_index.name">
                                <md-checkbox v-model="attributes.fog_index.checked"/>
                                <span class="md-list-item-text">{{ attributes.fog_index.name }}</span>
                            </md-list-item>
                            <md-divider></md-divider>
                            <md-list-item :key="attributes.avg_word_len.name">
                                <md-checkbox v-model="attributes.avg_word_len.checked"/>
                                <span class="md-list-item-text">{{ attributes.avg_word_len.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.avg_sentence_len.name">
                                <md-checkbox v-model="attributes.avg_sentence_len.checked"/>
                                <span class="md-list-item-text">{{ attributes.avg_sentence_len.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.sentence_len8_count.name">
                                <md-checkbox v-model="attributes.sentence_len8_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.sentence_len8_count.name }}</span>
                            </md-list-item>
                            <md-divider></md-divider>
                            <md-list-item :key="attributes.pr_coefficient.name">
                                <md-checkbox v-model="attributes.pr_coefficient.checked"/>
                                <span class="md-list-item-text">{{ attributes.pr_coefficient.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.qu_coefficient.name">
                                <md-checkbox v-model="attributes.qu_coefficient.checked"/>
                                <span class="md-list-item-text">{{ attributes.qu_coefficient.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.ac_coefficient.name">
                                <md-checkbox v-model="attributes.ac_coefficient.checked"/>
                                <span class="md-list-item-text">{{ attributes.ac_coefficient.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.din_coefficient.name">
                                <md-checkbox v-model="attributes.din_coefficient.checked"/>
                                <span class="md-list-item-text">{{ attributes.din_coefficient.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.con_coefficient.name">
                                <md-checkbox v-model="attributes.con_coefficient.checked"/>
                                <span class="md-list-item-text">{{ attributes.con_coefficient.name }}</span>
                            </md-list-item>
                        </md-list>
                    </div>
                    <div class="viewport">
                        <md-list>
                            <md-subheader>Реализация прагматикона языковой личности</md-subheader>
                            <md-list-item :key="attributes.uniform_rows_count.name">
                                <md-checkbox v-model="attributes.uniform_rows_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.uniform_rows_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.standalone_constructions_count.name">
                                <md-checkbox v-model="attributes.standalone_constructions_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.standalone_constructions_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.introductory_words_count.name">
                                <md-checkbox v-model="attributes.introductory_words_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.introductory_words_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.comparatives_count.name">
                                <md-checkbox v-model="attributes.comparatives_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.comparatives_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.syntax_splices_count.name">
                                <md-checkbox v-model="attributes.syntax_splices_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.syntax_splices_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.comparative_clauses_count.name">
                                <md-checkbox v-model="attributes.comparative_clauses_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.comparative_clauses_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.collation_clauses_count.name">
                                <md-checkbox v-model="attributes.collation_clauses_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.collation_clauses_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.epenthetic_constructions_count.name">
                                <md-checkbox v-model="attributes.epenthetic_constructions_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.epenthetic_constructions_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.complex_syntax_constructs_count.name">
                                <md-checkbox v-model="attributes.complex_syntax_constructs_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.complex_syntax_constructs_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.single_verb_count.name">
                                <md-checkbox v-model="attributes.single_verb_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.single_verb_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.appeal_count.name">
                                <md-checkbox v-model="attributes.appeal_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.appeal_count.name }}</span>
                            </md-list-item>
                        </md-list>
                    </div>
                    <div class="viewport">
                        <md-list>
                            <md-subheader>Описание тезауруса языковой личности</md-subheader>
                            <md-list-item :key="attributes.word_forms_count.name">
                                <md-checkbox v-model="attributes.word_forms_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.word_forms_count.name }}</span>
                            </md-list-item>
                            <md-list-item v-if="attributes.word_forms_count.checked === true">
                               <input v-model="normal_form" placeholder='Начальная форма'>
                            </md-list-item>
                            <md-list-item :key="attributes.keywords_count.name">
                                <md-checkbox v-model="attributes.keywords_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.keywords_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.bigrams_count.name">
                                <md-checkbox v-model="attributes.bigrams_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.bigrams_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.trigrams_count.name">
                                <md-checkbox v-model="attributes.trigrams_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.trigrams_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.dichotomy_pronouns_count.name">
                                <md-checkbox v-model="attributes.dichotomy_pronouns_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.dichotomy_pronouns_count.name }}</span>
                            </md-list-item>
                        </md-list>
                    </div>
                    <div class="viewport">
                        <md-list>
                            <md-subheader>Экспликация вербально-семантического уровня языковой личности</md-subheader>
                            <md-list-item :key="attributes.complex_words_count.name">
                                <md-checkbox v-model="attributes.complex_words_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.complex_words_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.modal_particles_count.name">
                                <md-checkbox v-model="attributes.modal_particles_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.modal_particles_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.interjections_count.name">
                                <md-checkbox v-model="attributes.interjections_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.interjections_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.modal_postfix_count.name">
                                <md-checkbox v-model="attributes.modal_postfix_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.modal_postfix_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.intensifiers_count.name">
                                <md-checkbox v-model="attributes.intensifiers_count.checked"/>
                                <span class="md-list-item-text">{{ attributes.intensifiers_count.name }}</span>
                            </md-list-item>
                            <md-list-item :key="attributes.errors.name">
                                <md-checkbox v-model="attributes.errors.checked"/>
                                <span class="md-list-item-text">{{ attributes.errors.name }}</span>
                            </md-list-item>
                        </md-list>
                    </div>
                </div>
                <div class="md-layout md-gutter md-alignment-center">
                    <md-button class="md-raised md-primary" :disabled="noAttributesSelected()"
                               @click="setDone('third_step', 'results_step')">Продолжить
                    </md-button>
                </div>
            </md-step>
            <md-step id="results_step" md-label="Результаты" md-description="Просмотр результатов"
                     :md-done.sync="results_step">

                <md-progress-spinner v-if="is_processing" :md-diameter="100" :md-stroke="10"
                                     md-mode="indeterminate"></md-progress-spinner>
                <md-empty-state
                        v-if='this.error && !this.is_processing'
                        md-icon="power_off"
                        md-label="Что-то пошло не так..."
                        md-description="Пожалуйста, повторите запрос">
                    <md-button class="md-raised md-primary" @click="setDone('third_step', 'results_step')">Повторить
                    </md-button>
                </md-empty-state>

                <template
                        v-if="results.pearson_correlation !== null || results.linear_regression !== null || results.student_correlation !== null">
                    <md-button class="md-raised md-primary" @click="csvExport">Выгрузить</md-button>
                    <md-button class="md-raised md-primary" @click="recalculateResults">Пересчитать</md-button>
                    <md-tabs class="md-primary" style="padding: 20px">
                        <md-tab id="results" md-label="Результаты">
                            <md-table class="content" :value="results.attributes" md-sort="id" md-sort-order="asc"
                                      md-fixed-header
                                      md-card>
                                <md-table-toolbar>
                                    <div class="md-toolbar-section-end" v-if="results.attributes">
                                        <md-list>
                                            <md-list-item v-if="results.pearson_correlation !== null">
                                                Коэффициент корреляции Пирсона: {{results.pearson_correlation}}
                                            </md-list-item>
                                            <md-list-item v-if="results.linear_regression !== null">
                                                Линейная регрессия:
                                                p-value - {{results.linear_regression.pvalue}},
                                                r-value - {{results.linear_regression.rvalue}},
                                                stderr - {{results.linear_regression.stderr}}
                                            </md-list-item>
                                            <md-list-item v-if="results.student_correlation !== null">
                                                t-критерий Стьюдента:
                                                p-value - {{results.student_correlation.pvalue}},
                                                statistic - {{results.student_correlation.statistic}}
                                            </md-list-item>
                                        </md-list>
                                        <md-list>
                                            <md-list-item v-if="results.keywords_correlation">
                                                Корреляция по ключевым словам: {{results.keywords_correlation}}
                                            </md-list-item>
                                            <md-list-item v-if="results.intensifiers_correlation">
                                                Корреляция по словам-интенсификаторам:
                                                {{results.intensifiers_correlation}}
                                            </md-list-item>
                                            <md-list-item v-if="results.bigrams_correlation">
                                                Корреляция по биграммам: {{results.bigrams_correlation}}
                                            </md-list-item>
                                            <md-list-item v-if="results.trigrams_correlation">
                                                Корреляция по триграммам: {{results.trigrams_correlation}}
                                            </md-list-item>
                                        </md-list>
                                    </div>
                                </md-table-toolbar>
                                <md-toolbar class="md-transparent" v-if="results.attributes.length === 0">
                                    <h6 class="md-title">Не выбраны параметры, участвующие в подсчете общего
                                        коэффициента корреляции </h6>
                                </md-toolbar>
                                <md-table-row slot="md-table-row" slot-scope="{ item }">
                                    <md-table-cell md-label="ID" md-sort-by="id" md-numeric>{{ item.id }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Атрибут" md-sort-by="description">{{ item.description }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Текст 1" md-sort-by="text1" md-numeric>{{ item.first_text
                                        }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Текст 2" md-sort-by="text2" md-numeric>{{ item.second_text
                                        }}
                                    </md-table-cell>
                                </md-table-row>

                            </md-table>
                        </md-tab>
                        <md-tab id="extended" md-label="Вспомогательные параметры">
                            <md-table class="content" :value="results.extended_attributes" md-sort="id"
                                      md-sort-order="asc"
                                      md-fixed-header
                                      md-card>
                                <md-table-row slot="md-table-row" slot-scope="{ item }" @click.native="onSelect(item)">
                                    <md-table-cell md-label="ID" md-sort-by="id" md-numeric>{{ item.id }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Атрибут" md-sort-by="name">{{ item.description }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Текст 1" md-sort-by="text1" md-numeric>{{
                                        item.first_text['value'] }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Текст 2" md-sort-by="text2" md-numeric>{{
                                        item.second_text['value'] }}
                                    </md-table-cell>
                                    <md-table-cell md-label="Просмотр">
                                        <md-icon
                                                v-if="(item.first_text.debug && item.first_text.debug.length > 0) || (item.second_text.debug && item.second_text.debug.length > 0)">
                                            visibility
                                        </md-icon>
                                        <md-icon
                                                v-if="(!item.first_text.debug || item.first_text.debug.length === 0) && (!item.second_text.debug || item.second_text.debug.length === 0)">
                                            visibility_off
                                        </md-icon>
                                    </md-table-cell>
                                </md-table-row>
                            </md-table>
                        </md-tab>
                    </md-tabs>
                </template>
            </md-step>
        </md-steppers>
        <md-toolbar md-elevation="0">
            <p style="margin: auto">© 2020, НИУ "Высшая школа экономики</p>
        </md-toolbar>
    </div>
</template>

import $backend from '../backend'

<script>

import $backend from '../backend'

export default {
  name: 'MainScreen',
  data: () => ({
    showDialog: false,
    selected: null,
    is_processing: true,
    error: '',
    active: 'first_step',
    first_step: false,
    second_step: false,
    third_step: false,
    results_step: false,
    first_text: '',
    normal_form: '',
    second_text: '',
    first_text_file: '',
    second_text_file: '',
    first_text_encoding: 'CP1251',
    second_text_encoding: 'CP1251',
    first_text_genre: 'fiction',
    second_text_genre: 'fiction',
    genres: [
      {text: 'художественная проза', value: 'fiction'},
      {text: 'сетевая литература', value: 'online_literature'},
      {text: 'сетевая публицистика', value: 'online_journalism'},
      {text: 'сетевая развлекательная публицистика', value: 'online_entertainment_journalism'},
      {text: 'корпоративная переписка', value: 'corporate_correspondence'}
    ],
    attributes: {
      'avg_word_len': {name: 'Средняя длина слова (в буквах)', checked: true},
      'avg_sentence_len': {name: 'Средняя длина предложения (в словах)', checked: true},
      'sentence_len8_count': {
        name: 'Количество предложений длиннее 8-ми слов',
        checked: true
      },
      'flesch_kincaid_index': {name: 'Индекс удобочитаемости Флеша-Кинкейда', checked: true},
      'fog_index': {name: 'Индекс туманности Ганнинга', checked: true},
      'pr_coefficient': {name: 'Коэффициент предметности (Pr)', checked: true},
      'qu_coefficient': {name: 'Коэффициент качественности (Qu)', checked: true},
      'ac_coefficient': {name: 'Коэффициент активности (Ас)', checked: true},
      'din_coefficient': {name: 'Коэффициент динамизма (Din)', checked: true},
      'con_coefficient': {name: 'Коэффициент связности текста (Con)', checked: true},
      'errors': {name: 'Количество слов несловарного написания', checked: true},
      'uniform_rows_count': {name: 'Предложения с однородными рядами', checked: true},
      'standalone_constructions_count': {name: 'Предложения с обособленными приложениями', checked: true},
      'introductory_words_count': {name: 'Вводные слова и конструкции', checked: true},
      'comparatives_count': {name: 'Целевые и выделительные обороты', checked: true},
      'comparatives_constructions_count': {name: 'Конструкции с семантикой сравнения', checked: true},
      'syntax_splices_count': {name: 'Синтаксические сращения', checked: true},
      'comparative_clauses_count': {name: 'Сравнительные придаточные', checked: true},
      'collation_clauses_count': {name: 'Конструкции с сопоставительными союзами', checked: true},
      'epenthetic_constructions_count': {name: 'Вставные конструкции', checked: true},
      'complex_syntax_constructs_count': {name: 'Сложные синтаксические конструкции', checked: true},
      'single_verb_count': {name: 'Глагольные односоставные предложения', checked: true},
      'appeal_count': {name: 'Обращения', checked: true},
      'dichotomy_pronouns_count': {name: 'Дихотомия "свой/чужой"', checked: true},
      'word_forms_count': {name: 'Количество употреблений форм слова', checked: true},
      'complex_words_count': {name: 'Сложные слова полуслитного написания', checked: true},
      'modal_particles_count': {name: 'Модальные частицы', checked: true},
      'interjections_count': {name: 'Междометия', checked: true},
      'modal_postfix_count': {name: 'Наличие/отсутствие модального постфикса «-то»', checked: true},
      'intensifiers_count': {name: 'Предпочтительные слова-интенсификаторы', checked: true},
      'keywords_count': {name: 'Ключевые слова', checked: true},
      'bigrams_count': {name: 'Наиболее частотные биграммы', checked: true},
      'trigrams_count': {name: 'Наиболее частотные триграммы', checked: true}
    },
    results: {
      'pearson_correlation': null,
      'linear_regression': null,
      'jaccard_correlation': null,
      'student_correlation': null,
      'keywords_correlation': null,
      'bigrams_correlation': null,
      'trigrams_correlation': null,
      'intensifiers_correlation': null,
      'attributes': [],
      'extended_attributes': []
    }
  }),
  methods: {
    setDone (id, index) {
      this[id] = true
      if (index) {
        this.active = index
      }
      if (index === 'results_step') {
        this.calculateResults()
      }
    },
    changeFirstTextEncoding () {
      console.log(this.first_text_file)
      const reader = new FileReader()

      reader.onload = e => { this.first_text = e.target.result }
      reader.readAsText(this.first_text_file, this.first_text_encoding)
    },
    changeSecondTextEncoding () {
      const reader = new FileReader()

      reader.onload = e => { this.second_text = e.target.result }
      reader.readAsText(this.second_text_file, this.second_text_encoding)
    },
    loadFirstTextFromFile (ev) {
      const file = ev.target.files[0]
      this.first_text_file = file
      const reader = new FileReader()

      reader.onload = e => { this.first_text = e.target.result }
      reader.readAsText(file, this.first_text_encoding)
    },
    loadSecondTextFromFile (ev) {
      const file = ev.target.files[0]
      this.second_text_file = file
      const reader = new FileReader()

      reader.onload = e => { this.second_text = e.target.result }
      reader.readAsText(file, this.second_text_encoding)
    },
    csvExport () {
      let csvContent = 'data:text/csv;charset=utf-8,'

      csvContent += [
        ['Коэффициент корреляции Пирсона', this.results.pearson_correlation].join(';'),
        '',
        'Линейная регрессия',
        ['p-value', this.results.linear_regression.pvalue].join(';'),
        ['r-value', this.results.linear_regression.rvalue].join(';'),
        ['stderr', this.results.linear_regression.stderr].join(';'),
        ['slope', this.results.linear_regression.slope].join(';'),
        ['intercept', this.results.linear_regression.intercept].join(';'),
        '',
        't-критерий Стьюдента',
        ['p-value', this.results.student_correlation.pvalue].join(';'),
        ['statistic', this.results.student_correlation.statistic].join(';'),
        '',
        ['Корреляция по ключевым словам', this.results.keywords_correlation || 'N/A'].join(';'),
        ['Корреляция по словам-интенсификаторам', this.results.intensifiers_correlation || 'N/A'].join(';'),
        ['Корреляция по биграммам', this.results.bigrams_correlation || 'N/A'].join(';'),
        ['Корреляция по триграммам', this.results.trigrams_correlation || 'N/A'].join(';'),
        '',
        'Относительные параметры',
        ['Номер параметра', 'Название параметра', 'Текст 1', 'Текст 2'].join(';'),
        ...this.results.attributes.map(item => Object.values(item).join(';')),
        '',
        'Абсолютные параметры',
        ['Номер параметра', 'Название параметра', 'Текст 1', 'Текст 2'].join(';'),
        ...this.results.extended_attributes.map(item => {
          let keys = Object.keys(item).filter(k => k !== 'name')
          return keys.map(k => (k === 'first_text' || k === 'second_text') ? item[k].value : item[k]).join(';')
        }
        )
      ]
        .join('\n')
        .replace(/(^\[)|(\]$)/gm, '')
      const data = encodeURI(csvContent)
      const link = document.createElement('a')
      link.setAttribute('href', data)
      link.setAttribute('download', 'export.csv')
      link.click()
    },
    noAttributesSelected () {
      return Object.keys(this.attributes).filter(key => this.attributes[key]['checked'] === true).length === 0
    },
    onSelect (item) {
      if (item !== undefined && ((item.first_text.debug && item.first_text.debug.length > 0) || (item.second_text.debug && item.second_text.debug.length > 0))) {
        this.selected = item || this.selected
        this.showDialog = true
      }
    },
    calculateResults () {
      this.error = ''
      this.is_processing = true
      this.results = {
        'pearson_correlation': null,
        'linear_regression': null,
        'jaccard_correlation': null,
        'student_correlation': null,
        'attributes': [],
        'keywords_correlation': null,
        'bigrams_correlation': null,
        'trigrams_correlation': null,
        'intensifiers_correlation': null,
        'extended_attributes': []
      }
      let payload = {
        'first_text': this.first_text,
        'first_text_genre': this.first_text_genre,
        'second_text': this.second_text,
        'second_text_genre': this.second_text_genre,
        'attributes': this.attributes,
        'normal_form': this.normal_form
      }
      $backend.calculateResults(payload)
        .then(responseData => {
          this.results = responseData['results']
          console.log(this.results)
          this.is_processing = false
        }).catch(error => {
          this.is_processing = false
          this.error = error.message
        })
    },
    recalculateResults () {
      this.error = ''
      this.is_processing = true
      let payload = {
        pearson_correlation: this.results.pearson_correlation,
        linear_regression: this.results.linear_regression,
        jaccard_correlation: this.results.jaccard_correlation,
        student_correlation: this.results.student_correlation,
        keywords_correlation: this.results.keywords_correlation,
        'bigrams_correlation': this.results.bigrams_correlation,
        'trigrams_correlation': this.results.trigrams_correlation,
        'intensifiers_correlation': this.results.intensifiers_correlation,
        'attributes': this.results.attributes,
        'extended_attributes': this.results.extended_attributes
      }
      this.results = {
        'pearson_correlation': null,
        'linear_regression': null,
        'jaccard_correlation': null,
        'student_correlation': null,
        'attributes': [],
        'keywords_correlation': null,
        'bigrams_correlation': null,
        'trigrams_correlation': null,
        'intensifiers_correlation': null,
        'extended_attributes': []
      }
      $backend.recalculateResults(payload)
        .then(responseData => {
          this.results = responseData['results']
          console.log(this.results)
          this.is_processing = false
        }).catch(error => {
          this.is_processing = false
          this.error = error.message
        })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
    h3 {
        margin: 40px 0 0;
    }

    ul {
        list-style-type: none;
        padding: 0;
    }

    li {
        display: inline-block;
        margin: 0 10px;
    }

    a {
        color: #42b983;
    }

    .content {
        padding: 20px;
    }

    .md-toolbar {
        margin-top: 16px;
        margin-bottom: 16px;
    }

    .md-progress-spinner {
        margin: 24px;
    }

    .viewport {
        width: 550px;
        max-width: 100%;
        display: inline-block;
        vertical-align: top;
        overflow: auto;
        padding-top: 30px;
        border: 1px solid rgba(#000, .12);

    }

    .md-toolbar + .md-toolbar {
        margin: auto;
    }
</style>

<style lang="css">
    .md-menu-content.md-select-menu {
        width: auto;
        max-width: none;
    }
</style>
