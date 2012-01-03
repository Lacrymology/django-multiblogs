from django.conf import settings
from django import template
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType

from multiblogs.models import Post

WITHOUT_SETS= getattr(settings, 'MULTIBLOGS_WITHOUT_SETS', False)
register = template.Library()

class GetStaffNode(template.Node):
    """
    Retrieves a list of active staff members
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        staff = Staff.active_objects.all()

        context[self.varname] = staff
        return ''

def get_active_staff(parser, token):
    """
    Retrieves a list of active staff members

    {% get_active_staff as staff %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as' 
    except AssertionError:
        raise template.TemplateSyntaxError('get_active_staff syntax: {% get_active_staff as varname %}')

    count = varname = None
    if argc == 3: t, a, varname = args
    elif argc == 4: t, count, a, varname = args

    return GetStaffNode(varname=varname)

register.tag(get_active_staff)

if not WITHOUT_SETS:
    def latest_entries(blog_set, blog, count=3):
        """
        Renders the latest `count` entries from `blog`
        """
        queryset=Post.published_objects.all().filter(
            blog__blog_set__slug=blog_set,
            blog__slug=blog).order_by('publish_date')[:count]
        return { 'entries': queryset }
else:
    def latest_entries(blog, count=3):
        queryset=(Post.published_objects.all().filter(blog__slug=blog)
                  .order_by('publish_date')[:count])
        return { 'entries': queryset }

register.inclusion_tag('multiblogs/latest_entries.html')(latest_entries)
