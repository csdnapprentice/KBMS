<template>
  <div class="demo-container">
    <div
        v-for="(item, index) in currentQuestion"
        :key="item.id"
    >
      <question-component
          :questionData="item"
          :chatHistory="item.chatHistory"
          @answer-submitted="handleAnswer"
          @update-note="handleNoteUpdate"
          @chat-message="handleChatMessage"
      />
    </div>
  </div>
</template>

<script>
import QuestionComponent from '@/components/QuestionComponent.vue';
import KnowledgePoint from "@/components/KnowledgePoint.vue";

export default {
  components: {KnowledgePoint, QuestionComponent },
  data() {
    return {
      currentQuestion: [
        // 单选题示例
        {
          content: JSON.stringify({
            stem: '## 单选题\nVue.js 的核心库主要关注什么？',
            type: 'single_choice',
            options: [
              {key: 'A', value: '视图层'},
              {key: 'B', value: '控制器层'},
              {key: 'C', value: '模型层'},
              {key: 'D', value: '数据持久层'}
            ],
            answer: 'A',
            explanation: 'Vue 的核心库聚焦**视图层**，采用自底向上增量开发的设计。'
          }),
          personal_note: '重要考点！需重点记忆',
          correct_count: 45,
          wrong_count: 12,
          chatHistory: []
        },

        // 多选题示例
        {
          content: JSON.stringify({
            stem: '## 多选题\n哪些是Vue的特性？（多选）',
            type: 'multiple_choice',
            options: [
              {key: 'A', value: '响应式数据'},
              {key: 'B', value: '虚拟DOM'},
              {key: 'C', value: 'JSX支持'},
              {key: 'D', value: '双向绑定'}
            ],
            answer: ['A', 'B', 'D'],
            explanation: 'JSX是React的特性，Vue默认使用模板语法'
          }),
          personal_note: '注意C选项是混淆项',
          correct_count: 28,
          wrong_count: 19,
          chatHistory: []
        },

        // 填空题示例
        {
          content: JSON.stringify({
            stem: '## 填空题\nVue的创始人是____，最新稳定版本是____',
            type: 'fill_blank',
            blanks: [
              {answer: '尤雨溪'},
              {answer: '3.4'}
            ],
            explanation: '尤雨溪(Evan You)是Vue.js的创建者'
          }),
          personal_note: '版本号需要定期更新',
          correct_count: 32,
          wrong_count: 8,
          chatHistory: []
        }
      ]
    };
  },

  methods: {
    handleAnswer(result) {
      console.log('答案提交:', result);
      // 更新题目统计（实际应发送到后端）
      if (result.isCorrect) {
        this.currentQuestion.correct_count++;
      } else {
        this.currentQuestion.wrong_count++;
      }
    },
    handleNoteUpdate(newNote) {
      console.log('更新笔记:', newNote);
      this.currentQuestion.personal_note = newNote;
    },
    handleChatMessage(message) {
      console.log('新聊天消息:', message);
      // 这里可以添加AI处理逻辑
    }
  }
};
</script>

<style>
.demo-container {
  max-width: 1200px;
  margin: 20px auto;
  background: #f5f7fb;
  padding: 20px;
  border-radius: 12px;
}
</style>