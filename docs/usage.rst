.. _usage:

Usage
=====

After installing multiblogs, there's only a few things to worry about.

If you do not want the infinite power of blog sets to go along with your multiple blogs, set:

```MULTIBLOGS_WITHOUT_SETS= TRUE```

In your settings.py file.

Also, in your urls add:

```
urlpatterns += patterns('',
    ...
    (r'^blogs/', include('multiblogs.urls')),
    ...
)
```

