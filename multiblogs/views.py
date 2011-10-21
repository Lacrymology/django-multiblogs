import logging
from django.conf import settings
from django.conf.urls.defaults import *
from django.template import loader, RequestContext
from django.views.generic import DetailView, ListView
from multiblogs.models import Blog, Post

WITHOUT_SETS= getattr(settings, 'MULTIBLOGS_WITHOUT_SETS', False)

if not WITHOUT_SETS:
    from multiblogs.models import BlogSet
    class BlogSetView(DetailView):
        model=BlogSet
        queryset=BlogSet.published_objects.all()
        template_name_field = 'template_name'
    

class BlogDetailView(DetailView):
    model=Blog
    template_name_field = 'template_name'

    def get_queryset(self):
        if not WITHOUT_SETS:
            queryset=Blog.published_objects.filter(blog_set__slug=self.kwargs['blog_set_slug'])
        else:
            queryset=Blog.published_objects.all()
        return queryset

class PostYearListView(ListView):
    model=Post
    template_name_field = 'blog__template_name'

    def get_queryset(self):
        if not WITHOUT_SETS:
            queryset=Post.published_objects.all().filter(blog__blog_set__slug=self.kwargs['blog_set_slug'], blog__slug=self.kwargs['blog_slug'], publish_date__year=self.kwargs['year'])
        else:
            queryset=Post.published_objects.all().filter(blog__slug=self.kwargs['slug'], publish_date__year=self.kwargs['year'])
        return queryset

class PostDetailView(DetailView):
    model=Post
    template_name_field = 'blog__template_name'

    def get_queryset(self):
        if not WITHOUT_SETS:
            queryset=Post.published_objects.all().filter(blog__blog_set__slug=self.kwargs['blog_set_slug'], blog__slug=self.kwargs['blog_slug'], publish_date__year=self.kwargs['year'])
        else:
            queryset=Post.published_objects.all().filter(blog__slug=self.kwargs['slug'], publish_date__year=self.kwargs['year'])
        return queryset
