from django.db import models


class Juz(models.Model):
    """Juz Model to inform which verse is which number."""
    # Note the 'lazy relationship' reference format here.
    juz_number = models.IntegerField(default=0)
    start_ayah = models.IntegerField(default=0)
    end_ayah = models.IntegerField(default=0)
    start_surah = models.IntegerField(default=0)
    end_surah = models.IntegerField(default=0)


class Surah(models.Model):
    """Surah Model with Many-to-One relationship with Ayah Model."""
    juz = models.IntegerField(default=0)
    name_en = models.CharField(max_length=32, null=True)
    name_ar = models.CharField(max_length=32, null=True)
    number = models.IntegerField(default=0)

    def __str__(self):
        return "{} ({})".format(self.name_en, self.number)


class Ayah(models.Model):
    """Ayah Model with Many-to-One relationship with AyahWord and Translation Models."""
    juz = models.IntegerField(default=0)
    chapter_id = models.ForeignKey(Surah, on_delete=models.PROTECT)
    verse_number = models.IntegerField()
    text_madani = models.CharField(max_length=2048)
    text_simple = models.CharField(max_length=2048)
    sajdah = models.BooleanField()

    def __str__(self):
        return "{}:{} ({})".format(self.chapter_id.number, self.verse_number, self.text_simple)


class AyahWord(models.Model):
    ayah = models.ForeignKey(Ayah, on_delete=models.PROTECT)
    text_madani = models.CharField(max_length=64, null=True)
    text_simple = models.CharField(max_length=64, null=True)
    class_name = models.CharField(max_length=32, default="p1")
    code = models.CharField(max_length=32)
    char_type = models.CharField(max_length=32, default="word")
    number = models.IntegerField(default=0)

    def __str__(self):
        return "{}:{}, {} ({})".format(self.ayah.chapter_id.number, self.ayah.verse_number,
                                       self.number, self.text_simple)


class Translation(models.Model):
    LANGUAGE_CHOICES = (
        ('EN', 'English'),
    )
    TRANSLATION_CHOICES = (
        ('transliteration', 'Transliteration'),
        ('itani', 'Itani'),
        ('shakir', 'Shakir'),
    )
    ayah = models.ForeignKey(Ayah, on_delete=models.PROTECT)
    language_name = models.CharField(choices=LANGUAGE_CHOICES, default='EN',
                                     max_length=32)
    resource_name = models.CharField(choices=TRANSLATION_CHOICES,
                                     default='transliteration', max_length=32)
    text = models.CharField(max_length=2048)

    def __str__(self):
        return "{}:{}, {} ()".format(self.ayah.chapter_id, self.ayah.verse_number,
                                     self.resource_name, self.text)
