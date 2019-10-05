from django.db.models.signals import post_save
from django.dispatch import receiver

from profiles.models import UserAyah, UserSurah
from quran.models import Ayah


@receiver(post_save, sender=UserAyah)
def check_surah_count(sender: UserAyah, instance: UserAyah, **kwargs) -> None:
    """Check that all ayahs in a Surah were recited after saving an Ayah.

    First we check to make sure all the ayahs in a Surah were recited by comparing the length of
    the User's ayahs with the length of the Surah's Ayahs.
    Then we find the least most recited Ayah and use that as a count of the number times the Surah
    was recited.
    """
    surah = instance.ayah.chapter_id
    surah_ayahs = Ayah.objects.filter(chapter_id=surah)
    num_ayahs = len(surah_ayahs)
    user = instance.user
    user_recited_ayahs_in_surah = UserAyah.objects.filter(
        user=user, ayah__chapter_id=surah).order_by('count')
    min_recited_count = user_recited_ayahs_in_surah[0].count
    user_ayahs = []
    # Convert all the Profile UserAyahs to Quran Ayahs
    for user_recited_ayah in user_recited_ayahs_in_surah:
        ayah = Ayah.objects.get(chapter_id=surah, id=user_recited_ayah.ayah.id)
        user_ayahs.append(ayah)
    num_user_ayahs = len(user_ayahs)
    # Did the user recite all the ayahs in the Surah?
    if num_ayahs == num_user_ayahs:
        # Update the count to the least recited number of Ayahs
        new_user_surah, created = UserSurah.objects.get_or_create(user=user, surah=surah)
        new_user_surah.count = min_recited_count
        new_user_surah.save()
