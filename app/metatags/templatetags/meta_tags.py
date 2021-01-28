from django import template
from metatags.models import MetaTags
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def meta_tags_include(path):
    meta_tag = MetaTags.objects.filter(url=path).first()
    if meta_tag:
        return mark_safe(
            '<meta name="description" content="{0}"> <meta name="keywords" content="{1}">'.format(meta_tag.description, meta_tag.keywords))

