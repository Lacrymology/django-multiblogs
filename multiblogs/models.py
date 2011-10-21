import logging
import mimetypes
import re

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager
from taggit.models import Tag
from articles.models import ArticleBase
from articles.decorators import logtime, once_per_instance
from markup_mixin.models import MarkupMixin
from django_extensions.db.models import TitleSlugDescriptionModel
from django_extensions.db.fields import AutoSlugField

from multiblogs.managers import PublishedManager, PublishedPostManager

log = logging.getLogger('multiblogs.models')

# Of course, blog sets are one of our key features. But what the hell,
# let's let you turn them off if you want to. Just set MULTIBLOGS_WITHOUT_SETS
# to True in your settings.py file.
WITHOUT_SETS= getattr(settings, 'MULTIBLOGS_WITHOUT_SETS', False)
AUTO_TAG = getattr(settings, 'MULTIBLOGS_AUTO_TAG', True)

if not WITHOUT_SETS:
    class BlogSet(MarkupMixin, TitleSlugDescriptionModel):
        published = models.BooleanField(_('Published'), default=True)
        rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)
        logo = models.ImageField(_('Logo'), blank=True, null=True, upload_to='multiblogs/blog_sets/logos/')
        template_name = models.CharField(_('template name'), max_length=255, blank=True, help_text=_("Example: 'multiblogs/blog_sets/art-class.html'. If this isn't provided, the system will use 'multiblogs/blog_set_detail.html'."))

        objects = models.Manager()
        published_objects = PublishedManager()
    
        def get_blogs(self, live=True, order_by='title'):
            '''
            Get all the blogs in this set that are live and orderd by their titles.
    
            Parameters include whether blogs should be live, and an ordering expression.
    
            Order can be any sortable field on the Blog model.
            '''
            return Blog.objects.filter(blog_set__slug=self.slug, published=live).order_by(order_by)
    
        def __unicode__(self):
            return self.title
            
        class Meta:
            verbose_name=_('Blog set')
            verbose_name_plural=_('Blog sets')
    
        class MarkupOptions:
            source_field = 'description'
            rendered_field = 'rendered_description'

class Blog(MarkupMixin, TitleSlugDescriptionModel):
    if not WITHOUT_SETS:
        blog_set = models.ForeignKey(BlogSet, blank=True, null=True)
    authors = models.ManyToManyField(User)
    published = models.BooleanField(_('Published'), default=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)
    logo = models.ImageField(_('Logo'), blank=True, null=True, upload_to='multiblogs/blogs/logos/')
    at_most = models.IntegerField('Show at most', default=5, help_text='Number of posts to show for this blog.')
    date_format = models.CharField('date format', max_length=30, default='F j, Y', help_text='Date format for this blog.')
    time_format = models.CharField('time format', max_length=30, default='g:i A', help_text='Time format for this blog.')
    template_name = models.CharField(_('template name'), max_length=255, blank=True, help_text=_("Example: 'multiblogs/blogs/whales-galore.html'. If this isn't provided, the system will use 'multiblogs/blog_detail.html'."))

    objects = models.Manager()
    published_objects = PublishedManager()

    def get_authors(self):
        '''
        Returns a string with each author's either full name or username, depending on what's available.
        '''
        authors = []
        for a in self.authors.all():
            if a.first_name or a.last_name:
                authors.append(a.first_name + " " + a.last_name)
            else:
                authors.append(a.username)
        
        # Cannot find user, return byline
        return ", ".join(authors)

    def get_posts(self, start=None, drafts=False, order_by='-publish_date', at_most=10):
        '''
        Get all the published posts in a blog.
        
        Parameters:
            start -- starting index for result set
            drafts -- True to return only drafts, False to return only published posts
            order_by -- expression specifying the order of the result set

        '''
        posts = Post.objects.filter(blog__slug=self.slug, publish_date__isnull=drafts)
        if start:
            posts = posts.filter(publish_date__gte=start)
        return posts.order_by(order_by)[:at_most]

    def get_post_count(self, drafts=False):
        '''
        Count all posts, published by default, but you can ask it to count all posts.
        '''
        return Post.objects.filter(blog__slug=self.slug, publish_date__isnull=drafts).count()

    def __unicode__(self):
        return self.title
        
    @models.permalink
    def get_absolute_url(self):
        if not WITHOUT_SETS:
            return ('mb-blog-detail', (self.blog_set.slug, self.slug))
        else:
            return ('mb-blog-detail', (self.slug))

    class Meta:
        verbose_name=_('Blog')
        verbose_name_plural=_('Blogs')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'

class Post(ArticleBase):
    blog = models.ForeignKey(Blog)
    tags = TaggableManager()
    auto_tag = models.BooleanField(default=AUTO_TAG, blank=True, help_text=_('Check this if you want to automatically assign any existing tags to this post based on its content.'))
    followup_for = models.ManyToManyField('self', symmetrical=False, blank=True, help_text=_('Select any other posts that this post follows up on.'), related_name='followups')
    related_posts = models.ManyToManyField('self', blank=True)

    objects = models.Manager()
    published_objects = PublishedPostManager()

    def get_attachments(self):
        return Attachment.objects.filter(post__slug=self.slug)

    def save(self, *args, **kwargs):
        requires_save=False
        super(Post, self).save()

        requires_save = self.do_auto_tag()
        requires_save |= self.do_tags_to_keywords()

        if requires_save:
            # bypass the other processing
            super(Post, self).save()

    @logtime
    @once_per_instance
    def do_auto_tag(self):
        """
        Performs the auto-tagging work if necessary.

        Returns True if an additional save is required, False otherwise.
        """

        if not self.auto_tag:
            log.debug('Post "%s" (ID: %s) is not marked for auto-tagging. Skipping.' % (self.title, self.pk))
            return False

        # don't clobber any existing tags!
        existing_ids = [t.id for t in self.tags.all()]
        log.debug('Post %s already has these tags: %s' % (self.pk, existing_ids))

        unused = Tag.objects.all()
        unused = unused.exclude(id__in=existing_ids)

        found = False
        to_search = (self.content, self.title, self.description, self.keywords)
        for tag in unused:
            regex = re.compile(r'\b%s\b' % tag.name, re.I)
            if any(regex.search(text) for text in to_search):
                log.debug('Applying Tag "%s" (%s) to Post %s' % (tag, tag.pk, self.pk))
                self.tags.add(tag)
                found = True

        return found

    def do_tags_to_keywords(self):
        """
        If meta keywords is empty, sets them using the article tags.

        Returns True if an additional save is required, False otherwise.
        """

        if len(self.keywords.strip()) == 0:
            self.keywords = ', '.join([t.name for t in self.tags.all()])
            return True

        return False

    @models.permalink
    def get_absolute_url(self):
        if not WITHOUT_SETS:
            return ('mb-post-detail', (self.blog.blog_set.slug, self.blog.slug, self.publish_date.year, self.slug))
        else:
            return ('mb-post-detail', (self.blog.slug, self.publish_date.year, self.slug))

class Attachment(models.Model):
    upload_to = lambda inst, fn: 'attach/%s/%s/%s' % (datetime.now().year, inst.post.slug, fn)

    post = models.ForeignKey(Post, related_name='attachments')
    attachment = models.FileField(upload_to=upload_to)
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('-post', 'id')

    def __unicode__(self):
        return u'%s: %s' % (self.post, self.caption)

    @property
    def filename(self):
        return self.attachment.name.split('/')[-1]

    @property
    def content_type_class(self):
        mt = mimetypes.guess_type(self.attachment.path)[0]
        log.info('Check content type %s', mt)
        if mt:
            content_type = mt.replace('/', '_')
        else:
            # assume everything else is text/plain
            content_type = 'text_plain'

        return content_type
        
