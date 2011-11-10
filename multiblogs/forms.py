import logging
from django.forms import ModelForm
from multiblogs.models import Post, Blog

class PostForm(ModelForm):
    class Meta:
        model = Post
        exclude = ('sites', 'keywords', 'slug', 'description', 'rendered_description', 'is_active', 'login_required', 'rendered_content', 'expiration_date', 'auto_tag', 'publish_date', 'followup_for', 'related_posts')

'''
    def save(self, *args, **kwargs):
        try:
            self.author_id = self.user.pk
            self.blog_id = Blog.objects.get(slug=kwargs['request'].path.split('/')[2]).pk
        except:
            pass
        super(PostForm, self).save(*args, **kwargs)
        '''
