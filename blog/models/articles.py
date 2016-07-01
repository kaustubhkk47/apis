from django.db import models

class Post(models.Model):
    author = models.ForeignKey('users.InternalUser', blank=True, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=False, null=False)

    show_online = models.BooleanField(default=True)
    delete_status = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return str(self.id) + '-' + self.title + '-' + self.author.name
