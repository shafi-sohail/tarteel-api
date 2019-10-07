# -*- coding: utf-8 -*-
import json
from operator import itemgetter
import os
from typing import Dict, Optional, List, Type, Union
from urllib.request import urlopen

import boto3
import botocore
from django.conf import settings
from whoosh.index import open_dir
from whoosh.qparser import AndGroup, OrGroup
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.qparser import FieldsPlugin, PhrasePlugin, SequencePlugin, WildcardPlugin
from whoosh.searching import Results, Searcher

from .special_cases import SPECIAL_CASES

BUCKET_NAME = 'tarteel-static'
s3 = boto3.client('s3',
                  aws_access_key_id=settings.AWS_ACCESS_KEY_S3,
                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_S3,
                  config=botocore.config.Config(s3={'addressing_style': 'path'}))


class Iqra(object):

    def __init__(self, directory='whooshdir'):
        root_dir = os.path.abspath(os.path.dirname(__file__))
        index_dir = os.path.join(root_dir, directory)
        self._ix = open_dir(index_dir)

    def _get_response_object_from_params(self,
                                         query_text: str,
                                         matches: Union[str, list],
                                         matched_terms: Union[str, list],
                                         suggestions: Union[str, list]) -> Dict:
        """Format parameters into a dictionary (JSON response)."""
        return {
            "queryText": query_text,
            "matches": matches,
            "matchedTerms": matched_terms,
            "suggestions": suggestions,
        }

    def _get_empty_response(self, value: str) -> Dict:
        """Utility wrapper for empty response."""
        return self._get_response_object_from_params(value, [], [], [])

    def _get_translation_from_url(self, translation: str, encoding: str = 'utf-8') -> List:
        """Downloads JSON from URL and converts it to a Python object.
        :param translation: Filename without the .json extension.
        :param encoding: The string encoding. Arabic uses utf-8.
        :return: The JSON as a Python object.
        """
        file = s3.get_object(Bucket=BUCKET_NAME, Key='iqra_quran/{}.json'.format(translation))
        json_str = file['Body'].read().decode(encoding)
        return json.loads(json_str)

    def _get_matches_from_results(self, results: Results, translation: str) -> List:
        """Return a list of matches sorted by Surah and Ayah number."""
        translated_quran_obj = self._get_translation_from_url(translation)

        final_matches = []
        for result in results:
            translation_ayah = translated_quran_obj[result['surah_num']-1][result['ayah_num']-1]
            final_matches.append({
                "surahNum": result['surah_num'],
                "ayahNum": result['ayah_num'],
                "translationSurahName": result['surah_name_en'],
                "arabicSurahName": result['surah_name_ar'],
                "translationAyah": translation_ayah,
                "arabicAyah": result['ayah']
            })
        return sorted(final_matches, key=itemgetter('surahNum', 'ayahNum'))

    def _parse_and_search(self,
                          searcher: Searcher,
                          content: str,
                          value: str,
                          limit: Optional[int] = None,
                          terms: bool = False,
                          group: Type[Union[AndGroup, OrGroup]] = OrGroup) -> Results:
        parser = QueryParser(content, self._ix.schema, group=group)
        parser.remove_plugin_class(FieldsPlugin)
        parser.remove_plugin_class(WildcardPlugin)
        query = parser.parse(value)
        return searcher.search(query, terms=terms, limit=limit)

    def get_special_cases_results(self, value: str, translation: str) -> Union[Dict, None]:
        """Takes in a query and compares it to hard-coded special cases.
        The special cases are for the "Miracle Letters"

        :param value: The ayah text.
        :param translation: The requested translation type
        :return: A list of ayah matches if there is a match, otherwise returns None
        :rtype: dict, None
        """
        matching_ayah_list = []
        for case in SPECIAL_CASES:
            if case[0] == value:
                value = case[1]
                matching_ayah_list = case[2]

        if len(matching_ayah_list) > 0:
            allowed_results = []
            for matching_ayah in matching_ayah_list:
                allowed_results.append("surah_num:{} AND ayah_num:{}".format(
                    str(matching_ayah[0]), str(matching_ayah[1])))

            parser = MultifieldParser(["surah_num", "ayah_num"], self._ix.schema)
            parser.remove_plugin_class(PhrasePlugin)
            parser.add_plugin(SequencePlugin())
            query = parser.parse(" OR ".join(allowed_results))
            with self._ix.searcher() as searcher:
                results = searcher.search(query, limit=7)
                return self._get_response_object_from_params(
                        value,
                        self._get_matches_from_results(results, translation),
                        [],
                        []
                )
        else:
            return None

    def get_result(self, value: str, translation: str, limit: Optional[int] = None) -> Dict:
        """ Checks to see if there are any special case results then searches for an Ayah with
        Whoosh if no special cases exist.

        :param value: The ayah text.
        :param translation: The type of translation.
        :param limit: The max limit on the number of queries to return.
        :return: A dictionary with query text, matches, matched terms, and suggestions.
        """
        # Start with special cases
        special_cases_results = self.get_special_cases_results(value, translation)
        if special_cases_results:
            return special_cases_results

        # Otherwise execute full search
        with self._ix.searcher() as searcher:
            # Check if its just one word
            is_single_word_query = False
            if len(value.split()) == 1:
                parser = MultifieldParser(
                        ["simple_ayah", "roots", "decomposed_ayah"], self._ix.schema
                )
                is_single_word_query = True
            else:
                parser = QueryParser("simple_ayah", self._ix.schema)
            # Execute search on a single word
            parser.remove_plugin_class(FieldsPlugin)
            parser.remove_plugin_class(WildcardPlugin)
            query = parser.parse(value)
            results = searcher.search(query, limit=limit)
            if results:
                final_matches = self._get_matches_from_results(results, translation)
                return self._get_response_object_from_params(
                    value,
                    final_matches,
                    value.split(' '),
                    []
                )

            if not is_single_word_query:
                results = self._parse_and_search(searcher, 'simple_ayah', value, limit, True)
                if not results:
                    results = self._parse_and_search(searcher, 'roots', value, limit, True)
                    if not results:
                        results = self._parse_and_search(searcher, 'decomposed_ayah', value,
                                                         limit, True)
                if results:
                    matched_terms = results.matched_terms()
                    first_results = None
                    if len(matched_terms) > 1 and results.scored_length() > 1:
                        if results[1].score > 10:
                            first_results = results
                        results = self._parse_and_search(searcher, 'simple_ayah',
                                                         results[0]['simple_ayah'], limit)
                    final_matches = self._get_matches_from_results(results, translation)

                    suggestions = []
                    if first_results:
                        for result in [fR for fR in first_results if fR.score > 10]:
                            suggestions.append(result['simple_ayah'])

                    return self._get_response_object_from_params(
                        value,
                        final_matches,
                        # `term` is a tuple where the second index contains the matching term.
                        [term[1] for term in matched_terms],
                        suggestions
                    )

        return self._get_empty_response(value)

    def get_translations(self, ayahs, translation: str):
        """Load the json file with the user's requested translation."""
        translated_quran_obj = self._get_translation_from_url(translation)
        for idx, ayahObj in enumerate(ayahs):
            surah_idx = ayahObj["surahNum"] - 1
            ayah_idx = ayahObj["ayahNum"] - 1
            ayahs[idx]["translationAyah"] = translated_quran_obj[surah_idx][ayah_idx]
        return ayahs
