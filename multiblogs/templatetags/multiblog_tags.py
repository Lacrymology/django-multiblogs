from django import template
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from classroom.models import Staff, School

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

class GetPrincipalNode(template.Node):
    """
    Retrieves a list of active principals
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        school = School.objects.get(primary=True)

        context[self.varname] = school.principal
        return ''

def get_active_principal(parser, token):
    """
    Retrieves a list of active principals

    {% get_active_principal as principal %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as' 
    except AssertionError:
        raise template.TemplateSyntaxError('get_active_principal syntax: {% get_active_principal as varname %}')

    count = varname = None
    if argc == 3: t, a, varname = args
    elif argc == 4: t, count, a, varname = args

    return GetPrincipalNode(varname=varname)

class GetSchoolNode(template.Node):
    """
    Retrieves the currently primary school
    """
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        school = School.objects.get(primary=True)

        context[self.varname] = school
        return ''

def get_primary_school(parser, token):
    """
    Retrieves the currently primary school

    {% get_primary_school as school %}
    """
    args = token.split_contents()
    argc = len(args)

    try:
        assert argc == 3 and args[1] == 'as' 
    except AssertionError:
        raise template.TemplateSyntaxError('get_primary_school syntax: {% get_primary_school as varname %}')

    varname = None
    t, a, varname = args

    return GetSchoolNode(varname=varname)

register.tag(get_primary_school)
register.tag(get_active_staff)
register.tag(get_active_principal)
