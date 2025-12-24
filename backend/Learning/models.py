# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class ChapterKnowledgeRelations(models.Model):
    chapter = models.OneToOneField('Chapters', models.DO_NOTHING, primary_key=True, db_comment='章节ID')  # The composite primary key (chapter_id, point_id) found, that is not supported. The first column is selected.
    point = models.ForeignKey('KnowledgePoints', models.DO_NOTHING, db_comment='知识点ID')

    class Meta:
        managed = False
        db_table = 'chapter_knowledge_relations'
        unique_together = (('chapter', 'point'),)
        db_table_comment = '章节-知识点关系表'


class ChapterQuestionRelations(models.Model):
    chapter = models.OneToOneField('Chapters', models.DO_NOTHING, primary_key=True, db_comment='章节ID')  # The composite primary key (chapter_id, question_id) found, that is not supported. The first column is selected.
    question = models.ForeignKey('Questions', models.DO_NOTHING, db_comment='问题ID')

    class Meta:
        managed = False
        db_table = 'chapter_question_relations'
        unique_together = (('chapter', 'question'),)
        db_table_comment = '章节-问题关系表'


class Chapters(models.Model):
    chapter_id = models.AutoField(primary_key=True, db_comment='章节ID')
    chapter_name = models.CharField(max_length=100, db_comment='章节名称')
    summary = models.TextField(blank=True, null=True, db_comment='个人总结')
    level = models.PositiveIntegerField(blank=True, null=True, db_comment='章节等级（1-5）')

    class Meta:
        managed = False
        db_table = 'chapters'
        db_table_comment = '章节表'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class KnowledgePoints(models.Model):
    point_id = models.AutoField(primary_key=True, db_comment='知识点ID')
    point_name = models.CharField(max_length=100, db_comment='知识点名称')
    content = models.TextField(db_comment='知识点内容')
    personal_understanding = models.TextField(blank=True, null=True, db_comment='个人理解')
    study_count = models.IntegerField(blank=True, null=True, db_comment='学习次数')

    class Meta:
        managed = False
        db_table = 'knowledge_points'
        db_table_comment = '知识点表'


class NoteChapterRelations(models.Model):
    note = models.OneToOneField('StudyNotes', models.DO_NOTHING, primary_key=True, db_comment='学习笔记ID')  # The composite primary key (note_id, chapter_id) found, that is not supported. The first column is selected.
    chapter = models.ForeignKey(Chapters, models.DO_NOTHING, db_comment='章节ID')

    class Meta:
        managed = False
        db_table = 'note_chapter_relations'
        unique_together = (('note', 'chapter'),)
        db_table_comment = '笔记-章节包含关系表'


class QuestionKnowledgeRelations(models.Model):
    question = models.OneToOneField('Questions', models.DO_NOTHING, primary_key=True, db_comment='问题ID')  # The composite primary key (question_id, point_id) found, that is not supported. The first column is selected.
    point = models.ForeignKey(KnowledgePoints, models.DO_NOTHING, db_comment='知识点ID')

    class Meta:
        managed = False
        db_table = 'question_knowledge_relations'
        unique_together = (('question', 'point'),)
        db_table_comment = '问题-知识点关系表'


class Questions(models.Model):
    question_id = models.AutoField(primary_key=True, db_comment='问题ID')
    content = models.JSONField(blank=True, null=True, db_comment='问题选项答案及解析（JSON格式）')
    wrong_count = models.IntegerField(blank=True, null=True, db_comment='错误次数')
    correct_count = models.IntegerField(blank=True, null=True, db_comment='正确次数')
    personal_note = models.TextField(blank=True, null=True, db_comment='答题记录')

    class Meta:
        managed = False
        db_table = 'questions'
        db_table_comment = '问题表'


class StudyNotes(models.Model):
    note_id = models.AutoField(primary_key=True, db_comment='学习笔记ID')
    note_name = models.CharField(max_length=100, db_comment='学习笔记名称')
    user = models.ForeignKey('Users', models.DO_NOTHING, db_comment='创建用户ID')
    created_at = models.DateTimeField(blank=True, null=True, db_comment='创建时间')
    icon = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'study_notes'
        db_table_comment = '学习笔记表'


class UserNoteRelations(models.Model):
    user = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True, db_comment='用户ID')  # The composite primary key (user_id, note_id) found, that is not supported. The first column is selected.
    note = models.ForeignKey(StudyNotes, models.DO_NOTHING, db_comment='学习笔记ID')

    class Meta:
        managed = False
        db_table = 'user_note_relations'
        unique_together = (('user', 'note'),)
        db_table_comment = '用户-笔记创建关系表'


class Users(models.Model):
    user_id = models.AutoField(primary_key=True, db_comment='用户ID')
    username = models.CharField(max_length=50, db_comment='用户名')
    account = models.CharField(unique=True, max_length=50, db_comment='账号（唯一）')
    password_hash = models.CharField(max_length=64, db_comment='密码哈希值（SHA-256）')

    class Meta:
        managed = False
        db_table = 'users'
        db_table_comment = '用户表'
