# -*- coding: utf-8 -*-
import json
from operator import itemgetter
import os
from urllib.request import urlopen
from whoosh.index import open_dir
from whoosh.qparser import (
    QueryParser, MultifieldParser, OrGroup, FieldsPlugin, WildcardPlugin,
    PhrasePlugin, SequencePlugin
)
from .special_cases import SPECIAL_CASES


class Iqra(object):

    def __init__(self, directory='whooshdir'):
        ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
        index_dir = os.path.join(ROOT_DIR, directory)
        self._ix = open_dir(index_dir)
        self._quranFilePath = 'https://s3.amazonaws.com/zappa-tarteel-static/iqra_quran/'

    def _getResponseObjectFromParams(self, queryText, matches, matchedTerms, suggestions):
        return {
            "queryText"   : queryText,
            "matches"     : matches,
            "matchedTerms": matchedTerms,
            "suggestions" : suggestions,
        }

    def _getEmptyResponse(self, value):
        return self._getResponseObjectFromParams(value, [], [], [])

    def _getTranslationFromURL(self, translation, encoding='utf-8'):
        """Downloads JSON from URL and converts it to python dict
        :param translation: Filename without the .json extension
        :type translation: str
        :return: The JSON as a python dict
        :rtype: dict
        """
        file_url = self._quranFilePath + translation + '.json'
        data_response = urlopen(file_url)
        json_data = data_response.read()
        json_str = json_data.decode(encoding)
        return json.loads(json_str)

    def _getMatchesFromResults(self, results, translation):
        translatedQuranObj = self._getTranslationFromURL(translation)

        finalMatches = []
        for result in results:
            finalMatches.append({
                "surahNum"            : result['surah_num'],
                "ayahNum"             : result['ayah_num'],
                "translationSurahName": result['surah_name_en'],
                "arabicSurahName"     : result['surah_name_ar'],
                "translationAyah"     : translatedQuranObj[result['surah_num'] - 1][
                    result['ayah_num'] - 1],
                "arabicAyah"          : result['ayah']
            })
        return sorted(finalMatches, key=itemgetter('surahNum', 'ayahNum'))

    def getSpecialCasesResults(self, value, translation):
        """Takes in a query and compares it to hard-coded special cases.
        The special cases are for the "Miracle Letters"

        :param translation: The requested translation type
        :type translation: str
        :return: A list of ayah matches if there is a match, otherwise returns None
        :rtype: list, None
        """
        matchingAyahList = []
        for case in SPECIAL_CASES:
            if case[0] == value:
                value = case[1]
                matchingAyahList = case[2]

        if len(matchingAyahList) > 0:
            allowedResults = []
            for matchingAyah in matchingAyahList:
                allowedResults.append(
                    "surah_num:" + str(matchingAyah[0]) + " AND ayah_num:" + str(
                            matchingAyah[1]))
            parser = MultifieldParser(["surah_num", "ayah_num"], self._ix.schema)
            parser.remove_plugin_class(PhrasePlugin)
            parser.add_plugin(SequencePlugin())
            query = parser.parse(" OR ".join(allowedResults))
            with self._ix.searcher() as searcher:
                results = searcher.search(query, limit=7)
                return self._getResponseObjectFromParams(
                        value,
                        self._getMatchesFromResults(results, translation),
                        [],
                        []
                )
        else:
            return None

    def getResult(self, value, translation):
        specialCasesResults = self.getSpecialCasesResults(value, translation)
        if specialCasesResults:
            return specialCasesResults

        with self._ix.searcher() as searcher:
            isSingleWordQuery = False
            if len(value.split()) == 1:
                parser = MultifieldParser(
                        ["simple_ayah", "roots", "decomposed_ayah"], self._ix.schema
                )
                isSingleWordQuery = True
            else:
                parser = QueryParser("simple_ayah", self._ix.schema)
            parser.remove_plugin_class(FieldsPlugin)
            parser.remove_plugin_class(WildcardPlugin)
            query = parser.parse(value)
            results = searcher.search(query, limit=None)
            if results:
                finalMatches = self._getMatchesFromResults(results, translation)
                return self._getResponseObjectFromParams(
                    value,
                    finalMatches,
                    value.split(' '),
                    []
                )

            if not isSingleWordQuery:
                parser = QueryParser("simple_ayah", self._ix.schema, group=OrGroup)
                parser.remove_plugin_class(FieldsPlugin)
                parser.remove_plugin_class(WildcardPlugin)
                query = parser.parse(value)
                results = searcher.search(query, terms=True, limit=None)
                if not results:
                    parser = QueryParser("roots", self._ix.schema, group=OrGroup)
                    parser.remove_plugin_class(FieldsPlugin)
                    parser.remove_plugin_class(WildcardPlugin)
                    query = parser.parse(value)
                    results = searcher.search(query, terms=True, limit=None)
                    if not results:
                        parser = QueryParser("decomposed_ayah", self._ix.schema, group=OrGroup)
                        parser.remove_plugin_class(FieldsPlugin)
                        parser.remove_plugin_class(WildcardPlugin)
                        query = parser.parse(value)
                        results = searcher.search(query, terms=True, limit=None)
                if results:
                    matchedTerms = results.matched_terms()

                    firstResults = None
                    if len(matchedTerms) > 1 and results.scored_length() > 1:
                        if results[1].score > 10:
                            firstResults = results

                        parser = QueryParser("simple_ayah", self._ix.schema)
                        parser.remove_plugin_class(FieldsPlugin)
                        parser.remove_plugin_class(WildcardPlugin)
                        query = parser.parse(results[0]["simple_ayah"])
                        results = searcher.search(query, limit=None)

                    finalMatches = self._getMatchesFromResults(results, translation)

                    suggestions = []
                    if firstResults:
                        for result in [fR for fR in firstResults if fR.score > 10]:
                            suggestions.append(result['simple_ayah'])

                    return self._getResponseObjectFromParams(
                        value,
                        finalMatches,
                        # term is a tuple where the second index contains the matching
                        # term
                        [term[1] for term in matchedTerms],
                        suggestions
                    )

        return self._getEmptyResponse(value)

    def getTranslations(self, ayahs, translation):
        # Load the json file with the user's requested translation
        translatedQuranObj = self._getTranslationFromURL(translation)
        for idx, ayahObj in enumerate(ayahs):
            surahIdx = ayahObj["surahNum"] - 1
            ayahIdx = ayahObj["ayahNum"] - 1
            ayahs[idx]["translationAyah"] = translatedQuranObj[surahIdx][ayahIdx]
        return ayahs