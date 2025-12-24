from django.urls import path
from . import  views
urlpatterns = [
    path('loginRegister', views.login_register, name='login_register'),
    path('getUsers', views.get_users, name='users'),
    path('getNotesById', views.user_get_notes_by_id, name='getBooksById'),
    path('getChaptersByNoteId', views.user_get_notes_by_noteId, name='getChapters'),
    path('addChapterByNoteId', views.user_add_chapter_by_noteId, name='addChapter'),
    path('aiTalkKnowledge', views.ai_talk_knowledge, name='aiTalkKnowledge'),
    path('getKnowledgeByNoteId', views.user_get_knowledge_by_noteId, name='getKnowledgeByNoteId'),
    path('updateKnowledgeByPointId', views.user_update_knowledge_by_point_id, name='updateKnowledgeByPointId'),
    path('addKnowledgeByChapterId',views.user_add_knowledge_by_chapter_id, name='addKnowledgeByChapterId'),
    path('getQuestionByNoteId', views.user_get_question_by_noteId, name='getQuestionByNoteId'),
    path('updateQuestion', views.user_update_question, name='updateQuestion'),
    path('addQuestion', views.user_add_Question_by_chapter_id, name='addQuestion'),
    path('addNote', views.user_add_note, name='addNote'),
    path('deleteQuestion', views.user_delete_question, name='deleteQuestion'),
]