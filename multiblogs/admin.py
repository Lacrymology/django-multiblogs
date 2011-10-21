import logging
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from articles.models import ArticleStatus
from taggit.models import Tag
from django.utils.translation import ugettext_lazy as _

WITHOUT_SETS= getattr(settings, 'MULTIBLOGS_WITHOUT_SETS', False)
if not WITHOUT_SETS: 
    from multiblogs.models import BlogSet
    admin.site.register(BlogSet)

from multiblogs.models import Blog, Post, Attachment

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 5
    max_num = 15

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog', 'status', 'author', 'publish_date',
                    'expiration_date', 'is_active')
    list_filter = ('author', 'status', 'is_active', 'publish_date',
                   'expiration_date', 'sites')
    list_per_page = 25
    search_fields = ('title', 'keywords', 'description', 'content')
    date_hierarchy = 'publish_date'
    inlines = [
        AttachmentInline,
    ]

    fieldsets = (
        (None, {'fields': ('title', 'blog', 'author', 'content', 'tags', 'auto_tag', 'markup', 'status')}),
        ('Metadata', {
            'fields': ('keywords', 'description',),
            'classes': ('collapse',)
        }),
        ('Relationships', {
            'fields': ('followup_for', 'related_posts'),
            'classes': ('collapse',)
        }),
        ('Scheduling', {'fields': ('publish_date', 'expiration_date')}),
        ('Advanced', {
            'fields': ('slug', 'is_active', 'login_required', 'sites'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ('followup_for', 'related_posts')
    prepopulated_fields = {'slug': ('title',)}

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
    mark_active.short_description = _('Mark select posts as active')

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
    mark_inactive.short_description = _('Mark select posts as inactive')

    def get_actions(self, request):
        actions = super(PostAdmin, self).get_actions(request)

        def dynamic_status(name, status):
            def status_func(self, request, queryset):
                queryset.update(status=status)

            status_func.__name__ = name
            status_func.short_description = _('Set status of selected to "%s"' % status)
            return status_func

        for status in ArticleStatus.objects.all():
            name = 'mark_status_%i' % status.id
            actions[name] = (dynamic_status(name, status), name, _('Set status of selected to "%s"' % status))

        def dynamic_tag(name, tag):
            def status_func(self, request, queryset):
                for article in queryset.iterator():
                    log.debug('Dynamic tagging: applying Tag "%s" to Article "%s"' % (tag, article))
                    article.tags.add(tag)
                    article.save()

            status_func.__name__ = name
            status_func.short_description = _('Apply tag "%s" to selected articles' % tag)
            return status_func

        for tag in Tag.objects.all():
            name = 'apply_tag_%s' % tag.pk
            actions[name] = (dynamic_tag(name, tag), name, _('Apply Tag: %s' % (tag.slug,)))

        return actions

    actions = [mark_active, mark_inactive]

    def save_model(self, request, obj, form, change):
        """Set the article's author based on the logged in user and make sure at least one site is selected"""

        try:
            author = obj.author
        except User.DoesNotExist:
            obj.author = request.user

        obj.save()

        # this requires an Article object already
        obj.do_auto_tag('default')
        form.cleaned_data['tags'] += list(obj.tags.all())

    def queryset(self, request):
        """Limit the list of articles to article posted by this user unless they're a superuser"""

        if request.user.is_superuser:
            return self.model._default_manager.all()
        else:
            return self.model._default_manager.filter(author=request.user)

admin.site.register(Blog)
admin.site.register(Post, PostAdmin)
