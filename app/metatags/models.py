from django.db import models


class MetaTags(models.Model):
    url = models.CharField(verbose_name='URL - Путь', unique=True, max_length=200,
                          help_text='Пример: "/about/contact/". Убедитесь, что ввели начальную и конечную косые черы.')
    keywords = models.CharField(verbose_name='Ключевые слова', max_length=255, help_text='Писать ключевые слова через запятую (с пробелом после запятой)')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'META-тег'
        verbose_name_plural = 'META-теги'

    def __str__(self):
        return self.url
