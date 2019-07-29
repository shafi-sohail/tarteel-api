from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import json
import os
from quran.models import Surah, Ayah, AyahWord, Translation
import urllib
from tqdm import tqdm

translation_filepath = '/Users/piraka/en/en_translation_'
shakir_baselink = 'http://www.everyayah.com/data/XML/English_Shakir' \
                  '/Quran_Translation_Shakir_'


def populate_itani():
    RESOURCE_NAME = 'itani'
    LANGUAGE_NAME = 'EN'
    for surah_num in tqdm(range(1, 115), desc='Surah'):
        filename = translation_filepath + str(surah_num) + '.json'

        with open(filename, encoding='utf-8') as json_file:
            surah_data = json.load(json_file)

            for verse_num, text in tqdm(surah_data['verse'].items(), desc='Ayah'):
                # Verse 0 is basmallah in all verses except al fatihah.
                verse_num = int(verse_num.lstrip('verse_'))
                if verse_num == 0:
                    continue
                try:
                    # Check if translation exists
                    new_translation = Translation.objects.get(
                            ayah__verse_number=verse_num,
                            ayah__chapter_id=surah_num,
                            text=text)
                    if new_translation:
                        print("Surah num: {}, Verse num: {} exists. Skipping...".format(
                            surah_num, verse_num))
                except Translation.DoesNotExist:
                    # Otherwise create it
                    ayah = Ayah.objects.get(chapter_id=surah_num,
                                            verse_number=verse_num)
                    new_translation = Translation(
                            ayah=ayah, resource_name=RESOURCE_NAME,
                            text=text, language_name=LANGUAGE_NAME)
                    new_translation.save()


def populate_shakir():
    RESOURCE_NAME = 'shakir'
    LANGUAGE_NAME = 'EN'
    for surah_num in tqdm(range(1, 115), desc='Surah'):
        num = str(surah_num).zfill(3)
        link = shakir_baselink + num + '.xml'
        request = urllib.request.urlopen(link)
        # file = request.read
        xml = BeautifulSoup(request)
        for ayah in tqdm(xml.find_all('aya'), desc='Ayah'):
            verse_num = ayah['id']
            text = ayah['text']
            try:
                new_translation = Translation.objects.get(
                            ayah__verse_number=verse_num,
                            ayah__chapter_id=surah_num,
                            text=text)
                if new_translation:
                    print("Surah num: {}, Verse num: {} exists. Skipping...".format(
                            surah_num, verse_num))
            except Translation.DoesNotExist:
                try:
                    ayah = Ayah.objects.get(chapter_id=surah_num,
                                            verse_number=verse_num)
                    new_translation = Translation(
                            ayah=ayah, resource_name=RESOURCE_NAME,
                            text=text, language_name=LANGUAGE_NAME)
                    new_translation.save()
                except Ayah.DoesNotExist:
                    print('Could not find ayah ({}:{})'.format(surah_num, verse_num))


class Command(BaseCommand):
    help = "Populates the quran database with translation information."

    def add_arguments(self, parser):
        parser.add_argument('--itani', action='store_true',
                            help='Populate Itani translation')

        parser.add_argument('--shakir', action='store_true',
                            help='Populate Shakir translation')

    def handle(self, *args, **options):
        if options['itani']:
            populate_itani()
        elif options['shakir']:
            populate_shakir()
