from django.contrib import admin
from Learning.models import *

# Register your models here.
admin.site.register(KnowledgePoints)
admin.site.register(Chapters)
admin.site.register(StudyNotes)
admin.site.register(Questions)
admin.site.register(Users)
admin.site.register(ChapterKnowledgeRelations)
admin.site.register(ChapterQuestionRelations)
admin.site.register(NoteChapterRelations)
admin.site.register(QuestionKnowledgeRelations)
admin.site.register(UserNoteRelations)


