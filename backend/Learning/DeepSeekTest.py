from openai import OpenAI
from LearningDjango.settings import DEEPSEEKAPI
client = OpenAI(api_key=DEEPSEEKAPI, base_url="https://api.deepseek.com")
myword = input("本人:")
messages = [{"role": "user", "content": myword}]
while myword != "结束":
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=False
    )
    print(response.choices[0].message)
    addmessages = {
        'role':response.choices[0].message.role,
        'content':response.choices[0].message.content
    }
    messages.append(addmessages)
    print(f"DeepSeek: {response.choices[0].message.content}")
    myword = input("本人:")
    messages.append(
        {"role": "user", "content": myword}
    )