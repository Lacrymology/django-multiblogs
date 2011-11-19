import logging
import mimetypes
import re

from datetime import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from taggit.managers import TaggableManager
from taggit.models import Tag
from articles.models import ArticleStatus
from articles.decorators import logtime, once_per_instance
from markup_mixin.models import MarkupMixin
from django_extensions.db.models import TitleSlugDescriptionModel
from django_extensions.db.fields import AutoSlugField
from django.template.defaultfilters import slugify, striptags

from multiblogs.managers import PublishedManager, PublishedPostManager

WORD_LIMIT=200
MARKUP_HTML = 'h'
MARKUP_MARKDOWN = 'm'
MARKUP_REST = 'r'
MARKUP_TEXTILE = 't'
MARKUP_OPTIONS = getattr(settings, 'MULTIBLOG_MARKUP_OPTIONS', (
        (MARKUP_HTML, _('HTML/Plain Text')),
        (MARKUP_MARKDOWN, _('Markdown')),
        (MARKUP_REST, _('ReStructured Text')),
        (MARKUP_TEXTILE, _('Textile'))
    ))
MARKUP_DEFAULT = getattr(settings, 'MULTIBLOG_MARKUP_DEFAULT', MARKUP_HTML)

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
    authors = models.ManyToManyField(User, related_name="authors")
    contributors=models.ManyToManyField(User, related_name="contributors", blank=True, null=True)
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

class PostManager(models.Manager):

    def active(self):
        """
        Retrieves all active articles which have been published and have not
        yet expired.
        """
        now = datetime.now()
        return self.get_query_set().filter(
                Q(expiration_date__isnull=True) |
                Q(expiration_date__gte=now),
                publish_date__lte=now,
                is_active=True)

    def live(self, user=None):
        """Retrieves all live articles"""

        qs = self.active()

        if user is not None and user.is_superuser:
            # superusers get to see all articles
            return qs
        else:
            # only show live articles to regular users
            return qs.filter(status__is_live=True)

MARKUP_HELP = _("""Select the type of markup you are using in this post.
<ul>
<li><a href="http://daringfireball.net/projects/markdown/basics" target="_blank">Markdown Guide</a></li>
<li><a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html" target="_blank">ReStructured Text Guide</a></li>
<li><a href="http://thresholdstate.com/articles/4312/the-textile-reference-manual" target="_blank">Textile Guide</a></li>
</ul>""")


class PostBase(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique_for_year='publish_date')
    status = models.ForeignKey(ArticleStatus, default=ArticleStatus.objects.default)
    author = models.ForeignKey(User)
    sites = models.ManyToManyField(Site, blank=True)

    keywords = models.TextField(blank=True, help_text=_("If omitted, the keywords will be the same as the article tags."))
    description = models.TextField(blank=True, help_text=_("If omitted, the description will be determined by the first bit of the article's content."))

    markup = models.CharField(max_length=1, choices=MARKUP_OPTIONS, default=MARKUP_DEFAULT, help_text=MARKUP_HELP)
    content = models.TextField()
    rendered_content = models.TextField()

    publish_date = models.DateTimeField(default=datetime.now, help_text=_('The date and time this article shall appear online.'))
    expiration_date = models.DateTimeField(blank=True, null=True, help_text=_('Leave blank if the article does not expire.'))

    is_active = models.BooleanField(default=True, blank=True)
    login_required = models.BooleanField(blank=True, help_text=_('Enable this if users must login before they can read this article.'))

    objects = PostManager()

    def __init__(self, *args, **kwargs):
        """Makes sure that we have some rendered content to use"""

        super(PostBase, self).__init__(*args, **kwargs)

        self._next = None
        self._previous = None
        self._teaser = None

        if self.id:
            # mark the article as inactive if it's expired and still active
            if self.expiration_date and self.expiration_date <= datetime.now() and self.is_active:
                self.is_active = False
                self.save()

            if not self.rendered_content or not len(self.rendered_content.strip()):
                self.save()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Renders the article using the appropriate markup language."""


        self.do_render_markup()
        self.do_meta_description()

        requires_save=False
        super(ArticleBase, self).save(*args, **kwargs)

        # do some things that require an ID first
        requires_save |= self.do_default_site(using)

        if requires_save:
            # bypass the other processing
            super(ArticleBase, self).save()

    def do_render_markup(self):
        """Turns any markup into HTML"""

        original = self.rendered_content
        if self.markup == MARKUP_MARKDOWN:
            self.rendered_content = markup.markdown(self.content)
        elif self.markup == MARKUP_REST:
            self.rendered_content = markup.restructuredtext(self.content)
        elif self.markup == MARKUP_TEXTILE:
            self.rendered_content = markup.textile(self.content)
        else:
            self.rendered_content = self.content

        return (self.rendered_content != original)


    def do_meta_description(self):
        """
        If meta description is empty, sets it to the article's teaser.

        Returns True if an additional save is required, False otherwise.
        """

        if len(self.description.strip()) == 0:
            self.description = self.teaser
            return True

        return False


    def do_default_site(self):
        """
        If no site was selected, selects the site used to create the article
        as the default site.

        Returns True if an additional save is required, False otherwise.
        """

        if not len(self.sites.all()):
            sites = Site.objects.all()
            if hasattr(sites, 'using'):
                sites = sites.using(using)
            self.sites.add(sites.get(pk=settings.SITE_ID))
            return True

        return False


    def _get_article_links(self):
        """
        Find all links in this article.  When a link is encountered in the
        article text, this will attempt to discover the title of the page it
        links to.  If there is a problem with the target page, or there is no
        title (ie it's an image or other binary file), the text of the link is
        used as the title.  Once a title is determined, it is cached for a week
        before it will be requested again.
        """

        links = []

        # find all links in the article
        log.debug('Locating links in article: %s' % (self,))
        for link in LINK_RE.finditer(self.rendered_content):
            url = link.group(1)
            log.debug('Do we have a title for "%s"?' % (url,))
            key = 'href_title_' + sha1(url).hexdigest()

            # look in the cache for the link target's title
            title = cache.get(key)
            if title is None:
                log.debug('Nope... Getting it and caching it.')
                title = link.group(2)

                if LOOKUP_LINK_TITLE:
                    try:
                        log.debug('Looking up title for URL: %s' % (url,))
                        # open the URL
                        c = urllib.urlopen(url)
                        html = c.read()
                        c.close()

                        # try to determine the title of the target
                        title_m = TITLE_RE.search(html)
                        if title_m:
                            title = title_m.group(1)
                            log.debug('Found title: %s' % (title,))
                    except:
                        # if anything goes wrong (ie IOError), use the link's text
                        log.warn('Failed to retrieve the title for "%s"; using link text "%s"' % (url, title))

                # cache the page title for a week
                log.debug('Using "%s" as title for "%s"' % (title, url))
                cache.set(key, title, 604800)

            # add it to the list of links and titles
            if url not in (l[0] for l in links):
                links.append((url, title))

        return tuple(links)
    links = property(_get_article_links)

    def _get_word_count(self):
        """Stupid word counter for an article."""

        return len(striptags(self.rendered_content).split(' '))
    word_count = property(_get_word_count)

    @models.permalink
    def get_absolute_url(self):
        return ('articles_display_article', (self.publish_date.year, self.slug))

    def _get_teaser(self):
        """
        Retrieve some part of the article or the article's description.
        """
        if not self._teaser:
            if len(self.description.strip()):
                text = self.description
            else:
                text = self.rendered_content

            words = text.split(' ')
            if len(words) > WORD_LIMIT:
                text = '%s...' % ' '.join(words[:WORD_LIMIT])
            self._teaser = text

        return self._teaser
    teaser = property(_get_teaser)


    class Meta:
        abstract=True

class Post(PostBase):
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
        self.do_unique_slug()

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

    def do_unique_slug(self):
        """
        Ensures that the slug is always unique for the year this article was
        posted
        """

        if not self.id:
            # make sure we have a slug first
            if not len(self.slug.strip()):
                self.slug = slugify(self.title)

            self.slug = self.get_unique_slug(self.slug)
            return True

        return False

    def get_unique_slug(self, slug):
        """Iterates until a unique slug is found"""

        # we need a publish date before we can do anything meaningful
        if type(self.publish_date) is not datetime:
            return slug

        orig_slug = slug
        year = self.publish_date.year
        counter = 1

        while True:
            not_unique = Post.objects.all()
            not_unique = not_unique.filter(publish_date__year=year, slug=slug)

            if len(not_unique) == 0:
                return slug

            slug = '%s-%s' % (orig_slug, counter)
            counter += 1


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
        
