import logging
from django.contrib import admin
from django.contrib.contenttypes import generic
from articles.admin import ArticleAdmin

from multiblogs.models import BlogSet, Blog, Post

admin.site.register(BlogSet)
admin.site.register(Blog)
admin.site.register(Post, ArticleAdmin)
