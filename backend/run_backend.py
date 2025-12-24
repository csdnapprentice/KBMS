import os
import sys

# 设置 Django 环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LearningDjango.settings")

# 将项目根目录添加到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import django
from django.core.management import execute_from_command_line

django.setup()

# 假设 manage.py 位于项目根目录（与 LearningDjango 文件夹同级）
execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])