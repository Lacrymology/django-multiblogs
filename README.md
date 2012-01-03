Django multiblogs
================== 

Built on the ArticleBase model in the One Cardinal fork of [django-articles](http://github.com/powellc/django-articles/), multiblogs
allows for multiple "sets" of blogs. Motivated by requests for both teacher and student blogs, and the need to have them segregated
on the website, multiblogs allows for multiple students to have their own blogs and to group them under one url.

URL examples of this scenario, when app is wired up to the base url of the site:

```
http://yourschool.com/student-voices/the-more-you-know/2011/our-new-principal/
http://yourschool.com/grade-7/fairys-and-goblins/2011/how-to-slay-werewolves/
http://yourschool.com/artsy-fartsy/photos-n-more/
```

Maybe you don't need blog sets? Just multiple different blogs. That's cool. Just go ahead and set your particluar blog to be part 
of no set and it will hookup to the default url:

http://yourschool.com/awesome-blog/2011/one-great-post/

Of course, you can't mix and match that kind of thing, as you need to set the variable ```MULTIBLOGS_WITHOUT_SETS = TRUE``` so that we
can properly re-route urls and what-not.

Install
---------

```
pip install django-multiblogs
```

Else you could follow whatever procedure you use to install python packakges (easy_install, etc)

Configuration
--------------

Currently there is little to configure. The important part is to wire it up in your django project:

```
INSTALLED_APPS = (
    ...
    'articles',
    'multiblogs',
    ...
)
```

Also, set:

```MULTIBLOGS_WITHOUT_SETS= TRUE```

If you do not want the infinite power of blog sets to go along with your multiple blogs.

In your urls:

```
urlpatterns += patterns('',
    ...
    (r'^blogs/', include('multiblogs.urls')),
    ...
)
```

Templates (& URLs)
--------------------

All templates go in a 'multiblogs' directory in your TEMPLATE_DIR:

```
blog_set_list.html (/)

blog_set_detail.html (/<blog-set-slug>/)

blog_detail.html (/<blog-set-slug>/<blog-slug>/)

post_year_archive.html (/<blog-set-slug>/<blog-slug>/<YYYY?year>/)

post_detail.html (/<blog-set-slug>/<blog-slug>/<YYYY?year>/<slug>/)
```

OPTIONAL SETTINGS
-----------------

```MULTIBLOGS_MARKUP_DEFAULT``` sets up the default markup option for blogs and posts. Options are:
'h' for HTML/Plain Text,
'm' for Markdown
'r' for ReStructured Text and
't' for Textile
(m, r and t require the corresponding python module).

If this option is not set, it defaults to another option: ```MARKUP_DEFAULT```,
which is actually an option for django-markup-mixin which is one of the
requirements of this app. For now, using MARKUP_DEFAULT is recommended, since I
still couldn't get MULTIBLOGS_MARKUP_DEFAULT to affect the blogs' defaults

```MULTIBLOGS_AUTO_TAG``` defines the default option for the auto-tag setting on posts. Defaults to True

```MULTIBLOG_HIDE_SLUGS``` defines whether the blog slugs should be visible and editable from the admin. Defaults to True

```MULTIBLOG_OVERRIDE_SLUGS``` defines whether the blog slugs should be overwritten on every save (in case the title changed). Defaults to False