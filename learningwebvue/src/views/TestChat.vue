<template>
  <ChatWindow
      :messages="chatHistory"
      @send="handleNewMessage"
  />
</template>

<script setup>
import { ref } from 'vue'
import { toRaw } from 'vue'
import ChatWindow from '@/components/ChatComponent.vue'

const chatHistory = ref([
  {
    role: 'user',
    content: '你好，我需要帮助...'
  },
  {
    role: 'assistant',
    content: '### 欢迎咨询！\n请详细描述您的问题...'
  }
])
const convertToDjangoFormat = (history) => {
  try {
    // 1. 解除响应式绑定
    const rawData = toRaw(history)

    // 2. 数据清洗
    const cleanedData = rawData.map(item => ({
      role: String(item.role).toLowerCase(),
      content: String(item.content)
    })).filter(item =>
        ['user', 'assistant', 'system'].includes(item.role)
    )

    // 3. 深拷贝序列化
    return JSON.parse(JSON.stringify(cleanedData))

  } catch (error) {
    console.error('转换失败:', error)
    return []
  }
}
const handleNewMessage = async (message) => {
  // 添加用户消息
  chatHistory.value.push({
    role: 'user',
    content: message
  })

  try {
    const url = `http://127.0.0.1:8000/users/aiTalkKnowledge`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify(chatHistory.value)
    })

    // 获取流阅读器
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    // 添加临时助手消息
    chatHistory.value.push({
      role: 'assistant',
      content: '',
      isLoading: true
    })
    // 获取最后一条消息的索引
    const lastIndex = chatHistory.value.length - 1

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      // 更新最后一条消息内容
      const chunk = decoder.decode(value)
      chatHistory.value[lastIndex].content += chunk

      // 强制触发Vue响应式更新（两种方式任选其一）
      // 方式1：使用数组解构
      // chatHistory.value = [...chatHistory.value]

      // 方式2：使用Vue的响应式API
      // import { triggerRef } from 'vue'
      // triggerRef(chatHistory)
    }

    // 流结束时更新状态
    chatHistory.value[lastIndex].isLoading = false

  } catch (error) {
    // 错误处理：移除临时消息并显示错误
    chatHistory.value.splice(-1, 1)
    console.error('请求失败:', error)
    // 可以添加错误消息
    chatHistory.value.push({
      role: 'system',
      content: `错误: ${error.message}`,
      isError: true
    })
  }
}
</script>