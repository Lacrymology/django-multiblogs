# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Blog'
        db.create_table('multiblogs_blog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='h', max_length=1)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', blank=True, populate_from='title', overwrite=False, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('published', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('rendered_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('at_most', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('date_format', self.gf('django.db.models.fields.CharField')(default='F j, Y', max_length=30)),
            ('time_format', self.gf('django.db.models.fields.CharField')(default='g:i A', max_length=30)),
            ('template_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('multiblogs', ['Blog'])

        # Adding M2M table for field authors on 'Blog'
        db.create_table('multiblogs_blog_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blog', models.ForeignKey(orm['multiblogs.blog'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('multiblogs_blog_authors', ['blog_id', 'user_id'])

        # Adding M2M table for field contributors on 'Blog'
        db.create_table('multiblogs_blog_contributors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('blog', models.ForeignKey(orm['multiblogs.blog'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('multiblogs_blog_contributors', ['blog_id', 'user_id'])

        # Adding model 'PostStatus'
        db.create_table('multiblogs_poststatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('is_live', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('multiblogs', ['PostStatus'])

        # Adding model 'Post'
        db.create_table('multiblogs_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['multiblogs.PostStatus'])),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('keywords', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='h', max_length=1)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('rendered_content', self.gf('django.db.models.fields.TextField')()),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('expiration_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('login_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('blog', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multiblogs.Blog'])),
            ('auto_tag', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('multiblogs', ['Post'])

        # Adding M2M table for field sites on 'Post'
        db.create_table('multiblogs_post_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm['multiblogs.post'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('multiblogs_post_sites', ['post_id', 'site_id'])

        # Adding M2M table for field followup_for on 'Post'
        db.create_table('multiblogs_post_followup_for', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_post', models.ForeignKey(orm['multiblogs.post'], null=False)),
            ('to_post', models.ForeignKey(orm['multiblogs.post'], null=False))
        ))
        db.create_unique('multiblogs_post_followup_for', ['from_post_id', 'to_post_id'])

        # Adding M2M table for field related_posts on 'Post'
        db.create_table('multiblogs_post_related_posts', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_post', models.ForeignKey(orm['multiblogs.post'], null=False)),
            ('to_post', models.ForeignKey(orm['multiblogs.post'], null=False))
        ))
        db.create_unique('multiblogs_post_related_posts', ['from_post_id', 'to_post_id'])

        # Adding model 'Attachment'
        db.create_table('multiblogs_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['multiblogs.Post'])),
            ('attachment', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('multiblogs', ['Attachment'])


    def backwards(self, orm):
        
        # Deleting model 'Blog'
        db.delete_table('multiblogs_blog')

        # Removing M2M table for field authors on 'Blog'
        db.delete_table('multiblogs_blog_authors')

        # Removing M2M table for field contributors on 'Blog'
        db.delete_table('multiblogs_blog_contributors')

        # Deleting model 'PostStatus'
        db.delete_table('multiblogs_poststatus')

        # Deleting model 'Post'
        db.delete_table('multiblogs_post')

        # Removing M2M table for field sites on 'Post'
        db.delete_table('multiblogs_post_sites')

        # Removing M2M table for field followup_for on 'Post'
        db.delete_table('multiblogs_post_followup_for')

        # Removing M2M table for field related_posts on 'Post'
        db.delete_table('multiblogs_post_related_posts')

        # Deleting model 'Attachment'
        db.delete_table('multiblogs_attachment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'multiblogs.attachment': {
            'Meta': {'ordering': "('-post', 'id')", 'object_name': 'Attachment'},
            'attachment': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['multiblogs.Post']"})
        },
        'multiblogs.blog': {
            'Meta': {'object_name': 'Blog'},
            'at_most': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'authors'", 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'contributors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'contributors'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'date_format': ('django.db.models.fields.CharField', [], {'default': "'F j, Y'", 'max_length': '30'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'h'", 'max_length': '1'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rendered_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'title'", 'overwrite': 'False', 'db_index': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'time_format': ('django.db.models.fields.CharField', [], {'default': "'g:i A'", 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'multiblogs.post': {
            'Meta': {'object_name': 'Post'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'auto_tag': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'blog': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multiblogs.Blog']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'followup_for': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'followups'", 'blank': 'True', 'to': "orm['multiblogs.Post']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'h'", 'max_length': '1'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'related_posts': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_posts_rel_+'", 'blank': 'True', 'to': "orm['multiblogs.Post']"}),
            'rendered_content': ('django.db.models.fields.TextField', [], {}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['multiblogs.PostStatus']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'multiblogs.poststatus': {
            'Meta': {'ordering': "('ordering', 'name')", 'object_name': 'PostStatus'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_live': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['multiblogs']
