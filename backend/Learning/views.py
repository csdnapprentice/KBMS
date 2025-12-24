import base64
import json
from django.utils import timezone

# Create your views here.
# views.py
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .apps import client
from .models import ChapterKnowledgeRelations, Questions
from .models import ChapterQuestionRelations
from .models import NoteChapterRelations, KnowledgePoints
from .models import StudyNotes, Chapters
from .models import Users


@csrf_exempt  # 临时禁用CSRF，正式项目建议用DRF或Token认证
def get_users(request):
    if request.method == 'GET':
        users = Users.objects.filter()
        data = [{"user_id": u.user_id, "name": u.username, "account":u.account, "password_hash":u.password_hash} for u in users]
        return JsonResponse({"code": 0, "data": data})

@csrf_exempt
def user_get_notes_by_id(request):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        study_notes = StudyNotes.objects.filter(user_id=user_id)
        data = []

        for study_note in study_notes:
            icon_data = None
            if study_note.icon:  # 直接访问 BinaryField
                try:
                    # 获取二进制数据
                    binary_data = bytes(study_note.icon)

                    # 生成 Data URL (直接使用 image/png，因为您确认全部是 PNG)
                    base64_str = base64.b64encode(binary_data).decode('utf-8')
                    icon_data = f"data:image/png;base64,{base64_str}"

                except Exception as e:
                    # 更详细的错误日志
                    print(f"Error processing icon for note {study_note.note_id}: {str(e)}")
                    # 可以选择返回 None 或一个默认的占位图标
                    icon_data = None

            data.append({
                "note_id": study_note.note_id,
                "note_name": study_note.note_name,
                "user_id": study_note.user_id,
                "created_at": study_note.created_at,
                "icon": icon_data  # 完整 Data URL
            })

        return JsonResponse({"code": 0, "data": data})

@csrf_exempt
def user_get_notes_by_noteId(request):
    if request.method == 'GET':
        note_id = request.GET.get('note_id')
        chapter_ids = NoteChapterRelations.objects.filter(
            note_id=note_id
        ).values_list('chapter_id', flat=True)
        data = []
        for chapter_id in chapter_ids:
            chapter = Chapters.objects.filter(chapter_id=chapter_id)
            chapter = chapter.first()
            data.append(
                {
                    "chapter_id":chapter.chapter_id,
                    "chapter_name":chapter.chapter_name,
                    "summary":chapter.summary,
                    "level":chapter.level
                }
            )
        return JsonResponse({"code": 0, "data": data})
@csrf_exempt
def user_add_chapter_by_noteId(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chapter_name = data.get('chapter_name')
        note_id = data.get('note_id')
        new_chapter = Chapters.objects.create(
            chapter_name=chapter_name,
            summary='',
            level=1
        )
        new_chapter_id = Chapters.objects.get(chapter_name=chapter_name).chapter_id
        new_chapter_note_relation = NoteChapterRelations.objects.create(
            note_id=note_id,
            chapter_id=new_chapter_id,
        )
        return JsonResponse({"code": 0})

@csrf_exempt
def ai_talk_knowledge(request):
    if request.method == 'POST':
        temperature = eval(request.GET.get('temperature'))
        print(temperature)
        data = request.body.decode('utf-8')
        data = json.loads(data)
        print(data)
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=data,
            stream=True,
            temperature=temperature
        )

        def stream():
            flag = 1
            for event in response:
                if event.choices[0].delta.reasoning_content is None:
                    if flag == 1:
                        flag = 0
                    yield event.choices[0].delta.content
                else:
                    yield event.choices[0].delta.reasoning_content  # 获取参数
        r = StreamingHttpResponse(streaming_content=stream(), content_type='text/event-stream')
        r['Cache-Control'] = 'no-cache'
        return r
@csrf_exempt
def user_get_knowledge_by_noteId(request):
    if request.method == 'GET':
        chapter_id = request.GET.get('chapter_id')
        point_ids = ChapterKnowledgeRelations.objects.filter(chapter_id=chapter_id).values_list('point_id', flat=True)
        data = []
        for point_id in point_ids:
            knowledge_point = KnowledgePoints.objects.filter(point_id=point_id)
            if knowledge_point.exists():
                knowledge_point = knowledge_point.first()
                addData = {
                    "point_id":knowledge_point.point_id,
                    "title":knowledge_point.point_name,
                    "content":knowledge_point.content,
                    "personalUnderstanding":knowledge_point.personal_understanding if knowledge_point.personal_understanding else "",
                    "studyCount":knowledge_point.study_count,
                }
                data.append(addData)
        return JsonResponse({"code": 0, "data": data})
@csrf_exempt
def user_get_question_by_noteId(request):
    if request.method == 'GET':
        chapter_id = request.GET.get('chapter_id')
        question_ids = ChapterQuestionRelations.objects.filter(chapter_id=chapter_id).values_list('question_id', flat=True)
        data = []
        for question_id in question_ids:
            knowledge_point = Questions.objects.filter(question_id=question_id)
            if knowledge_point.exists():
                knowledge_point = knowledge_point.first()
                addData = {
                    "content":knowledge_point.content,
                    "personal_note":knowledge_point.personal_note,
                    "correct_count":knowledge_point.correct_count,
                    "wrong_count":knowledge_point.wrong_count,
                    "question_id":knowledge_point.question_id,
                }
                data.append(addData)
        return JsonResponse({"code": 0, "data": data})
@csrf_exempt
def user_update_knowledge_by_point_id(request):
    if request.method == 'PUT':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        KnowledgePoints.objects.filter(
            point_id=data['point_id']
        ).update(
            point_name=data['title'],
            content=data['content'],
            personal_understanding=data.get('personalUnderstanding', ''),
            study_count=data['studyCount']
        )
        return JsonResponse({"code": 0, "data": data})
@csrf_exempt
def user_add_knowledge_by_chapter_id(request):
    if request.method == 'POST':
        chapter_id = request.GET.get('chapter_id')
        data = json.loads(request.body)
        newKnowledge = KnowledgePoints.objects.create(
            point_name=data['title'],
            content=data['content'],
            personal_understanding=data.get('personalUnderstanding', ''),
            study_count=data['studyCount']
        )
        ChapterKnowledgeRelations.objects.create(
            chapter_id=chapter_id,
            point_id=newKnowledge.point_id,
        )
        data['point_id'] = newKnowledge.point_id
        return JsonResponse({"code": 0,"data": data})
@csrf_exempt
def user_update_question(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        content = json.loads(data['content'])
        print(content)
        Questions.objects.filter(
            question_id=data['question_id']
        ).update(
            content=content,
            wrong_count=data['wrong_count'],
            correct_count=data.get('correct_count'),
            personal_note=data['personal_note'],
        )
        return JsonResponse({"code": 0, "data": data})
@csrf_exempt
def user_add_Question_by_chapter_id(request):
    if request.method == 'POST':
        chapter_id = request.GET.get('chapter_id')
        data = json.loads(request.body)
        content = json.loads(data['content'])
        newQuestion = Questions.objects.create(
            content=content,
            wrong_count=data['wrong_count'],
            personal_note=data.get('personal_note'),
            correct_count=data['correct_count'],
        )
        ChapterQuestionRelations.objects.create(
            chapter_id=chapter_id,
            question_id=newQuestion.question_id,
        )
        data['question_id'] = newQuestion.question_id
        print(data)
        return JsonResponse({"code": 0,"data": data})
@csrf_exempt
def user_add_note(request):
    if request.method == 'POST':
        # 从 request.POST 获取普通字段
        note_name = request.POST.get('note_name')
        user_id = request.POST.get('user_id')
        # 从 request.FILES 获取上传的文件
        icon_file = request.FILES.get('icon')
        # 检查必要参数是否存在
        if not (note_name and user_id and icon_file):
            return JsonResponse({"code": 1, "error": "Missing parameters"}, status=400)

        # 读取文件的二进制数据（假设使用 BinaryField）
        icon_data = icon_file.read()

        # 创建记录（假设 icon_path 是 BinaryField）
        StudyNotes.objects.create(
            note_name=note_name,
            icon=icon_data,
            user_id=user_id,
            created_at=timezone.now(),
        )

        return JsonResponse({"code": 0, "data": "success"})
@csrf_exempt
def user_delete_question(request):
    if request.method == 'DELETE':
        question_id = request.GET.get('questionId')
        print(question_id)
        question = Questions.objects.get(question_id=question_id)
        if question is not None:
            question.delete()
        return JsonResponse({"code": 0, "data": "success"})

@csrf_exempt
def login_register(request):
    if request.method == 'POST':
        try:
            # 解析请求体中的 JSON 数据
            data = json.loads(request.body)

            # 获取前端传递的参数
            username = data.get('username')
            password = data.get('password')
            captcha = data.get('captcha')
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'token': 'your_generated_token_here'  # 实际项目中应该生成真实的 token
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的 JSON 格式'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    # 只允许 POST 请求
    return JsonResponse({'success': False, 'message': '方法不允许'}, status=405)