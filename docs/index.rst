===================
Django Multiblogs
===================

Multiblogs is, like it's namesake the multiball mode of many
a classic pinball game, a way to inundate your site with blogs.
It was built in an academic environment, where the need was for
a classfull of students to each have their own blog.

What are we to do? The vast majority of django blog apps 
are rife with advertisments about "multiple authors support."
Well, multiple authors are one thing, but straight up multiple
blogs, with unique urls, feeds, and all that jazz? Nope.

So here we have multiblog, an app that allows groups of blogs
(like "students" or "faculty"), as well as multiple blogs:

http://mysite.com/blogs/students/joe-academic/

Of course, you can turn off the groups and just have a 
cornucopia of blogs too:

http://mysite.com/blogs/joe-academic/

This is still very much a work-in-progress, so read the docs,
kick the tires, and let me know what doesn't work.


Development
-----------

The source repository can be found at https://github.com/powellc/django-multiblogs


Contents
========

.. toctree::
 :maxdepth: 1

 changelog
 installation
 templatetags
 signals
 usage
 
