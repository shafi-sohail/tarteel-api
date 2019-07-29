from django.core.management.base import BaseCommand
import json
import os
from quran.models import Surah, Ayah, AyahWord, Translation, Juz
from tqdm import tqdm

juz_filepath = '/Users/piraka/tarteel_ws/tarteel-api/quran/management/commands/juz.json'


class Command(BaseCommand):
    help = "Populates the quran database with juz information."

    def handle(self, *args, **options):
        with open(juz_filepath, 'r') as json_file:
            juz_data = json.load(json_file)

            for i, juz_info in tqdm(enumerate(juz_data, start=1), desc='Juz'):
                juz_start_surah = juz_info['start']['index'].lstrip('0')
                juz_start_ayah = juz_info['start']['verse'].lstrip('verse_')
                juz_end_surah = juz_info['end']['index'].lstrip('0')
                juz_end_ayah = juz_info['end']['verse'].lstrip('verse_')

                start_surah = Surah.objects.get(number=juz_start_surah)
                start_ayah = Ayah.objects.get(chapter_id__number=juz_start_surah,
                                              verse_number=juz_start_ayah)
                end_surah = Surah.objects.get(number=juz_end_surah)
                end_ayah = Ayah.objects.get(chapter_id__number=juz_end_surah,
                                            verse_number=juz_end_ayah)

                new_juz = Juz(juz_number=i, start_ayah=start_ayah, end_ayah=end_ayah,
                              start_surah=start_surah, end_surah=end_surah)
                new_juz.save()

                for surah_num in range(juz_start_surah, juz_end_surah+1):
                    surah = Surah.objects.get(number=surah_num)
                    surah.juz = new_juz
                    surah.save()

                    # Get only ayahs greater than curr. ayah for starting surah
                    if surah_num == juz_start_surah:
                        surah_ayahs = Ayah.objects.filter(chapter_id__number=surah_num,
                                                          verse_number__gte=juz_start_ayah)
                    else:
                        surah_ayahs = Ayah.objects.filter(chapter_id__number=surah_num)

                    # Iterate over all ayahs and break when finished
                    for ayah in surah_ayahs:
                        if ayah.verse_number == juz_end_ayah and surah_num == \
                                juz_end_surah:
                            break
                        ayah.juz = new_juz
                        ayah.save()
