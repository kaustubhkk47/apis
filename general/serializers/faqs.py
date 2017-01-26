
def serialize_faq_entry(faqentry):
	faqentrydict = {}
	faqentrydict["question"] = faqentry.question
	faqentrydict["answer"] = faqentry.answer
	return faqentrydict