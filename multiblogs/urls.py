from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView

from multiblogs.models import Blog, Post
from multiblogs.views import BlogDetailView, PostYearListView, PostDetailView

WITHOUT_SETS= getattr(settings, 'MULTIBLOGS_WITHOUT_SETS', False)
if not WITHOUT_SETS: 
    from multiblogs.models import BlogSet
    from multiblogs.views import BlogSetView
    urlpatterns = patterns('',
        url(r'^$', view=ListView.as_view(model=BlogSet, queryset=BlogSet.published_objects.all()),name="mb-blog-set-list"),
        url(r'^(?P<slug>[-\w]+)/$', view=BlogSetView.as_view(),name="mb-blog-set-detail"),
    	url(r'^(?P<blog_set_slug>[-\w]+)/(?P<slug>[-\w]+)/$', view=BlogDetailView.as_view(), name='mb-blog-detail'),
    	url(r'^(?P<blog_set_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<year>[\d]+)/$', view=PostYearListView.as_view(), name='mb-post-year-archive'),
    	url(r'^(?P<blog_set_slug>[-\w]+)/(?P<blog_slug>[-\w]+)/(?P<year>[\d]+)/(?P<slug>[-\w]+)/$', view=PostDetailView.as_view(), name='mb-post-detail'),
    )

else:
    urlpatterns = patterns('',
    	url(r'^(?P<slug>[-\w]+)/$', view=BlogDetailView.as_view(), name='mb-blog-detail'),
    	url(r'^(?P<slug>[-\w]+)/(?P<year>[\d]+)/$', view=PostYearListView.as_view(), name='mb-post-year-archive'),
    	url(r'^(?P<blog_slug>[-\w]+)/(?P<year>[\d]+)/(?P<slug>[-\w]+)/$', view=PostDetailView.as_view(), name='mb-post-detail'),
    )

