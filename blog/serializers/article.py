from users.serializers.internalUser import serialize_internaluser

def parseArticles(ArticleQuerySet, parameters = {}):

	Articles = []

	for Article in ArticleQuerySet:
		ArticleEntry = serializeArticle(Article, parameters)
		Articles.append(ArticleEntry)

	return Articles

def serializeArticle(articleEntry, parameters = {}):
	article = {}

	article["articleID"] = articleEntry.id
	article["title"] = articleEntry.title
	article["slug"] = articleEntry.slug
	article["show_online"] = articleEntry.show_online
	article["delete_status"] = articleEntry.delete_status
	article["created_at"] = articleEntry.created_at
	article["updated_at"] = articleEntry.updated_at

	if "article_details" in parameters and parameters["article_details"] == 1:
		article["linkedin_pulse_link"] = articleEntry.linkedin_pulse_link
		article["medium_link"] = articleEntry.medium_link
		article["tumblr_link"] = articleEntry.tumblr_link
		article["quora_link"] = articleEntry.quora_link
		article["blogspot_link"] = articleEntry.blogspot_link

	if hasattr(articleEntry, "author"):
		if "internal_user_details" in parameters and parameters["internal_user_details"] == 1:
			article["author"] = serialize_internaluser(articleEntry.author)
		else:
			author = {}
			author["internaluserID"] = articleEntry.author.id
			author["name"] = articleEntry.author.name
			article["author"] = author

	return article

