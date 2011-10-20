from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView
from multiblogs.models import BlogSet, Blog, Post


# custom views vendors
urlpatterns = patterns('',
    url(r'^$', 
        view=ListView.as_view(
            model=BlogSet, 
            queryset=BlogSet.published_objects.all()), 
            name="mb-blog-set-list"),
    url(r'^(?P<slug>[-\w]+)/$', 
        view=DetailView.as_view(
            model=BlogSet, 
            queryset=BlogSet.published_objects.all()), 
            name="mb-blog-set-detail"),

	url(r'^(?P<blog-set-slug>[-\w]+)/(?P<slug>[-\w]+)/$', 
        view=DetailView.as_view(
            model=Blog, 
            queryset=Blog.objects.filter(blog_set__slug=blog-set-slug), 
            name="mb-blog-detail"),

	url(r'^(?P<blog-set-slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<year>[\d]+)/$', 
        view=ListView.as_view(
            model=Post, 
            queryset=Post.published_objects.filter(blog__blog_set__slug=blog-set-slug, blog__slug=slug, publish_date__year=year), 
            name="mb-post-year-archive"),

	url(r'^(?P<blog-set-slug>[-\w]+)/(?P<blog-slug>[-\w]+)/(?P<year>[\d]+)/(?P<slug>[-\w]+)/$', 
        view=DetailView.as_view(
            model=Post, 
            queryset=Post.published_objects.filter(blog__blog_set__slug=blog-set-slug, blog__slug=slug, publish_date__year=year), 
            name="mb-post-detail"),
)
