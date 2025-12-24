from django.apps import AppConfig
from openai import OpenAI

from LearningDjango.settings import DEEPSEEKAPI

client = OpenAI(api_key=DEEPSEEKAPI, base_url="https://api.deepseek.com")
class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Learning'
