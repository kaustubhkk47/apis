from django.db import models

from scripts.utils import validate_bool

class Article(models.Model):
    author = models.ForeignKey('users.InternalUser', blank=True, null=True)
    title = models.CharField(max_length=255, blank=False, null=False)
    slug = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=False, null=False)

    show_online = models.BooleanField(default=True)
    delete_status = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    linkedin_pulse_link = models.TextField(blank=True,null=True)
    medium_link = models.TextField(blank=True,null=True)
    tumblr_link = models.TextField(blank=True,null=True)
    quora_link = models.TextField(blank=True,null=True)
    blogspot_link = models.TextField(blank=True,null=True)

    class Meta:
        ordering = ['-id']

    def __unicode__(self):
        return str(self.id) + '-' + self.title + '-' + self.author.name

def filterArticles(parameters):
    articles = Article.objects.filter(delete_status=False)

    if "articlesArr" in parameters:
        articles = articles.filter(id__in=parameters["articlesArr"])

    if "show_online" in parameters:
        articles = articles.filter(show_online=parameters["show_online"])

    #if "internalusersArr" in parameters:
    #    articles = articles.filter(author_id__in=parameters["internalusersArr"])

    return articles

def validateArticleData(article, old_article, is_new):

    flag = 0

    if not "title" in article or article["title"]==None:
        flag = 1
        article["title"] = old_article.title
    if not "content" in article or article["content"]==None:
        flag = 1
        article["content"] = old_article.content
    if not "show_online" in article or not validate_bool(article["show_online"]):
        article["show_online"] = old_article.show_online
    if not "linkedin_pulse_link" in article or article["linkedin_pulse_link"]==None:
        article["linkedin_pulse_link"] = old_article.linkedin_pulse_link
    if not "medium_link" in article or article["medium_link"]==None:
        article["medium_link"] = old_article.medium_link
    if not "tumblr_link" in article or article["tumblr_link"]==None:
        article["tumblr_link"] = old_article.tumblr_link
    if not "quora_link" in article or article["quora_link"]==None:
        article["quora_link"] = old_article.quora_link
    if not "blogspot_link" in article or article["blogspot_link"]==None:
        article["blogspot_link"] = old_article.blogspot_link

    if is_new == 1 and flag == 1:
        return False

    return True

def populateArticleData(articlePtr, article):
    articlePtr.title = article["title"]
    articlePtr.slug = article["slug"]
    articlePtr.content = article["content"]
    articlePtr.show_online = int(article["show_online"])
    articlePtr.linkedin_pulse_link = article["linkedin_pulse_link"]
    articlePtr.medium_link = article["medium_link"]
    articlePtr.tumblr_link = article["tumblr_link"]
    articlePtr.quora_link = article["quora_link"]
    articlePtr.blogspot_link = article["blogspot_link"]