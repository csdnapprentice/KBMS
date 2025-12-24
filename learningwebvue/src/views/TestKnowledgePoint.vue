<script setup>
import { ref } from 'vue';
import KnowledgePoint from "@/components/KnowledgePoint.vue";

// 示例知识数据
const knowledge = ref({
  title: 'Vue 3 组件开发',
  content: `## 组件基础\nVue 3 组件采用Composition API...\n\`\`\`javascript\nexport default {\n  setup() {}\n}\n\`\`\``,
  personalUnderstanding: '### 个人心得\n组件开发需要注意props的类型验证...',
  studyCount: 12
});

// 示例聊天记录
const chatMessages = ref([
  { content: '请解释Vue的响应式原理', role: 'user' },
  { content: 'Vue 3使用Proxy实现响应式...', role: 'ai' }
]);

// 提交处理
const handleSubmit = async (updatedData) => {
  try {
    // 这里模拟API调用
    const response = await fetch('/api/knowledge', {
      method: 'PUT',
      body: JSON.stringify(updatedData)
    });

    if (response.ok) {
      // 更新本地数据
      knowledge.value = {
        ...knowledge.value,
        ...updatedData
      };
    }
  } catch (error) {
    console.error('更新失败:', error);
  }
};

// 学习完成处理
const handleStudyComplete = () => {
  knowledge.value.studyCount += 1;
  // 这里可以添加实际API调用
};

// 处理AI消息
const handleChatMessage = async (message) => {
  // 添加用户消息
  chatMessages.value.push({ content: message, role: 'user' });

  try {
    // 模拟AI回复
    const aiResponse = '这是模拟的AI回复...';
    chatMessages.value.push({ content: aiResponse, role: 'ai' });

    // 实际应该调用AI接口
    // const response = await fetch('/api/chat', {
    //   method: 'POST',
    //   body: JSON.stringify({ message })
    // });
    // const data = await response.json();
    // chatMessages.value.push({ content: data.reply, role: 'ai' });
  } catch (error) {
    console.error('聊天请求失败:', error);
  }
};
</script>

<template>
  <KnowledgePoint
      :title="knowledge.title"
      :content="knowledge.content"
      :personal-understanding="knowledge.personalUnderstanding"
      :study-count="knowledge.studyCount"
      :chat-history="chatMessages"
      @submit="handleSubmit"
      @study-complete="handleStudyComplete"
      @chat-message="handleChatMessage"
  />
</template>

<style scoped>
/* 添加临时样式测试容器可见性 */
.knowledge-container {
  border: 2px solid red;
  min-height: 500px;
}
</style>