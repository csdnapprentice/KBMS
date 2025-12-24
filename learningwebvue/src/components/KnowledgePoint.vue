<template>
  <div class="knowledge-container">
    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 标题部分 -->
      <div v-if="!isEditing" class="header">
        <div class="header-left">
          <h1>{{ title }}</h1>
          <div class="action-buttons">
            <button class="icon-button" @click="toggleEdit">✎</button>
            <button class="icon-button" @click="increaseStudyCount">✔</button>
          </div>
        </div>
        <button class="ai-trigger" @click="toggleAI">
          {{ showAI ? '关闭AI解析' : '打开AI解析' }}
        </button>
      </div>
      <div v-else class="edit-form">
        <input v-model="editTitle" class="edit-input" />
        <textarea v-model="editContent" class="edit-textarea" />
        <textarea v-model="editPersonal" class="edit-textarea" />
        <div class="edit-buttons">
          <button @click="saveEdit">提交</button>
          <button @click="toggleEdit">取消</button>
        </div>
      </div>

      <!-- 内容展示 -->
      <div v-if="!isEditing">
        <!-- 内容展示 -->
        <div v-if="!isEditing">
          <!-- 内容部分 -->
          <div class="content-section">
            <markdown-renderer :content="content" />
          </div>

          <!-- 个人理解 -->
          <div class="toggle-section">
            <div class="toggle-header" @click="showPersonal = !showPersonal">
              <h3>个人理解</h3>
              <span>{{ showPersonal ? '▼' : '▶' }}</span>
            </div>
            <div v-if="showPersonal" class="markdown-content">
              <markdown-renderer :content="personalUnderstanding" />
            </div>
          </div>

          <!-- 学习次数 -->
          <div class="study-count">
            <span>学习次数: {{ studyCount }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="ai-sidebar" :class="{ active: showAI }">
      <div class="sidebar-content">
        <ChatWindow
            :messages="chatHistory"
            @send="handleNewMessage"
        />
      </div>
    </div>
  </div>
</template>
<style scoped>
.knowledge-container {
  display: flex;
  flex: 1;
  min-width: 0; /* 关键：允许内容压缩 */
  position: relative;
  background: #fff;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: 100vh;
}

.main-content {
  flex: 1;
  min-width: 0;
  padding: 24px;
  overflow-y: auto;
  transition: all 0.3s;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.header-left h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 1rem;
}

.icon-button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #f0f4ff, #e8ebf5);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.icon-button:hover {
  background: linear-gradient(135deg, #e3e9ff, #dde2f0);
  transform: translateY(-1px);
}

.ai-trigger {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #8a63d2, #6c42b5);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.ai-trigger:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(108, 66, 181, 0.2);
}

.edit-form {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.edit-input {
  width: 100%;
  padding: 12px;
  margin-bottom: 1.5rem;
  border: 2px solid #e0e4e9;
  border-radius: 8px;
  font-size: 1.2rem;
  transition: border-color 0.3s ease;
}

.edit-input:focus {
  outline: none;
  border-color: #6c42b5;
}

.edit-textarea {
  width: 100%;
  height: 200px;
  padding: 15px;
  margin-bottom: 1.5rem;
  border: 2px solid #e0e4e9;
  border-radius: 8px;
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
}

.edit-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.edit-buttons button {
  padding: 10px 25px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.edit-buttons button:first-child {
  background: linear-gradient(135deg, #6c42b5, #8a63d2);
  color: white;
}

.edit-buttons button:last-child {
  background: #f0f4ff;
  color: #666;
}

.content-section {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  line-height: 1.7;
}

.toggle-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.toggle-header {
  padding: 1.5rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background 0.3s ease;
  width:auto;
}

.toggle-header:hover {
  background: #f8f9ff;
}

.study-count {
  text-align: right;
  color: #888;
  font-size: 0.9rem;
  padding: 1rem;
}

.knowledge-container {
  justify-content: center;
}
.ai-sidebar {
  width: 0;
  height: calc(100vh - 32px); /* 保持与激活状态相同的高度计算 */
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: #fff;
  border-left: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 16px;
  align-self: flex-start;
  will-change: width; /* 启用硬件加速 */
  backface-visibility: hidden; /* 防止渲染抖动 */
}

.ai-sidebar.active {
  width: 600px;
  min-width: 400px;
}

@media (max-width: 1200px) {
  .ai-sidebar.active {
    width: 300px;
    min-width: 300px;
  }
}
/* 新增关键帧动画 */
@keyframes sidebarSlide {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 新增响应式处理 */
@media (max-width: 1400px) {
  .main-content {
    margin-left: 20px; /* 小屏幕时保持间距 */
    margin-right: 20px;
  }
}

@media (max-width: 768px) {
  .main-content {
    min-width: calc(100vw - 40px); /* 移动端保持全宽 */
    margin-left: 20px;
    margin-right: 20px;
  }

  .ai-sidebar.active {
    flex-basis: 300px; /* 移动端侧边栏稍窄 */
  }
}
.markdown-content {
  font-family: 'Inter', sans-serif;
  line-height: 1.8;
}

.markdown-content h2 {
  color: #2c3e50;
  margin-top: 1.5em;
}

.markdown-content pre {
  background: #f8f9ff;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-content code {
  font-family: 'Fira Code', monospace;
  background: #f8f9ff;
  padding: 2px 6px;
  border-radius: 4px;
}
.sidebar-content {
  flex: 1;
  min-height: 0; /* 允许内容压缩 */
  display: flex;
  flex-direction: column;
  position: relative; /* 新增 */
  max-height: 100%; /* 限制最大高度 */
}
</style>
<script>
import ChatWindow from '@/components/ChatComponent.vue';
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'
export default {
  components: { ChatWindow,MarkdownRenderer },
  props: {
    title: String,
    content: String,
    personalUnderstanding: String,
    studyCount: Number,
    chatHistory: Array
  },
  data() {
    return {
      showPersonal: false,
      showAI: false,
      isEditing: false,
      editTitle: this.title,
      editContent: this.content,
      editPersonal: this.personalUnderstanding
    };
  },
  methods: {
    // 移除 compiledMarkdown 方法
    toggleEdit() {
      this.isEditing = !this.isEditing;
      if (!this.isEditing) {
        this.editTitle = this.title;
        this.editContent = this.content;
        this.editPersonal = this.personalUnderstanding;
      }
    },
    async saveEdit() {
      try {
        await this.$emit('submit', {
          title: this.editTitle,
          content: this.editContent,
          personalUnderstanding: this.editPersonal
        });
        this.isEditing = false;
      } catch (error) {
        console.error('保存失败:', error);
      }
    },
    increaseStudyCount() {
      this.$emit('study-complete');
    },
    handleNewMessage(message) {
      this.$emit('chat-message', message);
    },
    toggleAI() {
      this.showAI = !this.showAI;
    }
  }
};
</script>