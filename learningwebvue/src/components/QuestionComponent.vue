<template>
  <div class="question-container">
    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="header">
        <div class="header-left">
          <div class="action-buttons">
            <button class="icon-button" @click="toggleNoteEdit">✎ 编辑</button>
            <!-- 添加的删除按钮 -->
            <button class="icon-button delete-button" @click="deleteQuestion">🗑 删除</button>
          </div>
        </div>
        <button class="ai-trigger" @click="toggleAI">
          {{ showAI ? '关闭AI解析' : '打开AI解析' }}
        </button>
      </div>

      <!-- 题目展示区域 -->
      <div class="question-content" v-if="!showNoteEditor">
        <!-- 题目题干 -->
        <div class="markdown-content">
          <MarkdownRenderer :content="parsedContent.stem"/>
        </div>

        <!-- 在单选选择题部分添加class绑定 -->
        <div v-if="questionType === 'single_choice'" class="options-container">
          <div v-for="(option, index) in parsedContent.options"
               :key="index"
               class="option-item"
               :class="[
         { 'selected': selectedAnswer === option.key },
         { 'correct': hasSubmitted && option.key === parsedContent.answer },
         { 'incorrect': hasSubmitted && selectedAnswer === option.key && selectedAnswer !== parsedContent.answer }
       ]"
               @click="handleSelect(option.key)">
            <span class="option-key">{{ option.key }}.</span>
            <div class="markdown-content">
            <markdown-renderer class="option-value" :content="option.value" />
            </div>
          </div>
        </div>

        <!-- 在多选选择题部分添加class绑定 -->
        <div v-if="questionType === 'multiple_choice'" class="options-container">
          <div v-for="(option, index) in parsedContent.options"
               :key="index"
               class="option-item"
               :class="[
         { 'selected': selectedAnswer.includes(option.key) },
         { 'correct': hasSubmitted && parsedContent.answer.includes(option.key) },
         { 'incorrect': hasSubmitted && selectedAnswer.includes(option.key) && !parsedContent.answer.includes(option.key) }
       ]"
               @click="handleMultiSelect(option.key)">
            <span class="option-key">{{ option.key }}.</span>
            <div class="markdown-content">
            <markdown-renderer class="option-value" :content="option.value" />
            </div>
          </div>
        </div>

        <!-- 在填空题部分添加class绑定和方法调用 -->
        <!-- 修改填空部分模板 -->
        <div v-if="questionType === 'fill_blank'" class="fill-blank-container">
          <div v-for="(blank, index) in parsedContent.blanks"
               :key="index"
               class="blank-item">
    <textarea v-model="userAnswers[index]"
              :placeholder="`填空 ${index + 1}`"
              :disabled="hasSubmitted"
              class="blank-input"
              :class="{
                'correct': hasSubmitted && isBlankCorrect(index),
                'incorrect': hasSubmitted && !isBlankCorrect(index)
              }"
              rows="1"></textarea>
            <span class="correct-answer" v-if="hasSubmitted">
      正确答案: <markdown-renderer :content="parsedContent.blanks[index].answer"/>
    </span>
          </div>
        </div>

        <!-- 答案解析 -->
        <div v-if="showExplanation" class="explanation-section">
          <h3>题目解析</h3>
          <div class="markdown-content"><markdown-renderer :content="parsedContent.explanation"/></div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button v-if="!hasSubmitted"
                  class="submit-button"
                  :disabled="!isAnswerSelected"
                  @click="submitAnswer">
            提交答案
          </button>
          <button v-else class="reset-button" @click="resetQuestion">
            重置题目
          </button>
        </div>

        <!-- 统计信息 -->
        <div class="stats-section">
          <span>正确次数: {{ correctCount }}</span>
          <span>错误次数: {{ wrongCount }}</span>
        </div>

        <!-- 个人笔记 -->
        <div class="personal-note">
          <h3 @click="toggleNoteSection">个人笔记
            <span>{{ showNote ? '▼' : '▶' }}</span>
          </h3>
          <div v-if="showNote" class="markdown-content"><markdown-renderer :content="parsedPersonalNote"/></div>
        </div>
      </div>

      <!-- 编辑界面 -->
      <div v-if="showNoteEditor" class="editor-container">
        <div class="editor-section">
          <h3>编辑个人笔记</h3>
          <textarea v-model="editNote" class="editor-textarea" placeholder="输入你的笔记..."></textarea>
        </div>

        <div class="editor-section">
          <h3>编辑题目内容（JSON格式）</h3>
          <textarea v-model="editContent"
                    class="editor-textarea json-editor"
                    placeholder="输入题目JSON内容..."></textarea>
        </div>

        <div class="editor-buttons">
          <button class="save-button" @click="saveEdits">保存所有更改</button>
          <button class="cancel-button" @click="toggleNoteEdit">取消</button>
        </div>
      </div>
    </div>

    <!-- AI侧边栏 -->
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

<script>
import ChatWindow from '@/components/ChatComponent.vue';
import MarkdownRenderer from '@/components/MarkdownRenderer.vue';

export default {
  components: { ChatWindow, MarkdownRenderer },
  props: {
    questionData: {
      type: Object,
      required: true
    },
    chatHistory: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      showAI: false,
      hasSubmitted: false,
      selectedAnswer: null,
      userAnswers: [],
      showNote: true,
      showNoteEditor: false,
      editNote: '',
      editContent: '',
      showExplanation: false
    };
  },
  watch: {
    questionData: {
      immediate: true,
      deep: true,
      handler(newVal, oldVal) {
        // 只有当题目内容变化时才重置答题状态
        const oldContent = oldVal ? oldVal.content : ''
        const newContent = newVal.content || ''

        this.editNote = newVal.personal_note || ''
        this.editContent = newContent

        if (newContent !== oldContent) {
          this.resetQuestionState()
        }
      }
    }
  },
  computed: {
    parsedContent() {
      try {
        return JSON.parse(this.questionData.content);
      } catch (e) {
        console.error('题目解析错误:', e);
        return {
          stem: '题目解析错误，请检查内容格式',
          options: [],
          explanation: '',
          type: 'single_choice',
          blanks:[],
          answer:''
        };
      }
    },
    questionType() {
      return this.parsedContent.type || 'single_choice';
    },
    isAnswerSelected() {
      switch(this.questionType) {
        case 'single_choice': return !!this.selectedAnswer;
        case 'multiple_choice': return this.selectedAnswer.length > 0;
        case 'fill_blank': return this.userAnswers.every(a => a?.trim());
        default: return false;
      }
    },
    correctCount() {
      return this.questionData.correct_count || 0;
    },
    wrongCount() {
      return this.questionData.wrong_count || 0;
    },
    parsedPersonalNote() {
      return this.questionData.personal_note || '暂无笔记';
    }
  },
  methods: {
    deleteQuestion() {
      if (confirm('确定要删除这道题目吗？')) {
        this.$emit('delete');
      }
    },
    isBlankCorrect(index) {
      return this.userAnswers[index]?.trim().toLowerCase() ===
          this.parsedContent.blanks[index].answer.toLowerCase();
    },
    // 题目交互方法
    handleSelect(key) {
      if (!this.hasSubmitted) {
        this.selectedAnswer = key;
      }
    },
    handleMultiSelect(key) {
      if (!this.hasSubmitted) {
        const index = this.selectedAnswer.indexOf(key);
        if (index === -1) {
          this.selectedAnswer.push(key);
        } else {
          this.selectedAnswer.splice(index, 1);
        }
      }
    },
    submitAnswer() {
      let isCorrect = false;
      switch(this.questionType) {
        case 'single_choice':
          this.$emit('addUsersAnswer', this.selectedAnswer)
          isCorrect = this.selectedAnswer === this.parsedContent.answer;
          break;
        case 'multiple_choice':
          this.$emit('addUsersAnswer', this.selectedAnswer)
          isCorrect = JSON.stringify([...this.selectedAnswer].sort()) ===
              JSON.stringify([...this.parsedContent.answer].sort());
          break;
        case 'fill_blank':
          // 确保 userAnswers 和 blanks 数量一致
          if (this.userAnswers.length !== this.parsedContent.blanks?.length) {
            isCorrect = false;
            break;
          }

          isCorrect = this.userAnswers.every((ans, i) => {
            const blank = this.parsedContent.blanks?.[i];
            if (!blank || !blank.answer) return false;

            const userAnswer = (ans || '').trim().toLowerCase();
            const correctAnswer = blank.answer.trim().toLowerCase();
            return userAnswer === correctAnswer;
          });
          break;
      }

      this.showExplanation = true;
      this.hasSubmitted = true;
      this.$emit('answer-submitted', { isCorrect });
    },
    resetQuestion() {
      this.hasSubmitted = false;
      this.selectedAnswer = this.questionType === 'multiple_choice' ? [] : null;
      this.userAnswers = [];
      this.showExplanation = false;
    },

    // 笔记和编辑相关方法
    toggleNoteSection() {
      this.showNote = !this.showNote;
    },
    toggleNoteEdit() {
      this.showNoteEditor = !this.showNoteEditor;
      if (!this.showNoteEditor) {
        this.resetEdits();
      }
    },
    resetEdits() {
      this.editNote = this.questionData.personal_note || '';
      this.editContent = this.questionData.content || '';
    },
    saveEdits() {
      try {
        // 验证题目内容格式
        JSON.parse(this.editContent);
        // 触发更新事件
        this.$emit('update-note', this.editNote);
        this.$emit('update-content', this.editContent);
        this.showNoteEditor = false;
      } catch (e) {
        alert(`题目内容格式错误：${e.message}`);
      }
    },

    // 其他方法
    toggleAI() {
      this.showAI = !this.showAI;
    },
    handleNewMessage(message) {
      this.$emit('chat-message', message);
    },
    resetQuestionState() {
      this.resetQuestion();
      this.showExplanation = false;
    }
  }
};
</script>

<style scoped>
.question-container {
  display: flex;
  flex: 1;
  min-width: 0;
  position: relative;
  background: #fff;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  height: calc(100vh - 100px);
  max-width: 100vw;
  overflow-x: hidden;
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

.icon-button {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  background: linear-gradient(135deg, #f0f4ff, #e8ebf5);
  color: #6c42b5;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
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

/* 题目内容样式 */
.question-stem {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.options-container {
  display: grid;
  gap: 12px;
  margin: 20px 0;
}

.option-item {
  padding: 16px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid #e0e4e9;
  display: flex;
  align-items: center;
}


.option-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108,66,181,0.1);
}

.option-item.selected {
  border-color: #6c42b5;
  background: #f8f5ff;
}

.option-key {
  font-weight: 700;
  color: #6c42b5;
  margin-right: 12px;
  min-width: 30px;
}

/* 编辑界面样式 */
.editor-container {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.editor-section {
  margin-bottom: 32px;
}

.editor-section h3 {
  color: #6c42b5;
  margin-bottom: 12px;
}

.editor-textarea {
  width: 90%;
  padding: 16px;
  border: 2px solid #e0e4e9;
  border-radius: 8px;
  min-height: 150px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;     /* 强制换行 */
  word-wrap: break-word;     /* 支持单词中断 */
  overflow-wrap: anywhere;   /* 更积极的换行策略 */
}

.json-editor {
  min-height: 300px;
  /* 新增以下样式 */
  white-space: pre-wrap;       /* 允许保留空格换行 */
  word-break: break-word;     /* 长单词换行 */
  font-family: 'Courier New', monospace; /* 等宽字体更好对齐 */
  line-height: 1.6;           /* 增加行高 */
  tab-size: 2;                /* 设置缩进尺寸 */
  padding: 1em;               /* 增加内边距 */
  overflow-x: auto;           /* 允许横向滚动代替隐藏 */
}

.editor-buttons {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}

.save-button {
  background: #6c42b5;
  color: white;
  padding: 12px 24px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
}

.cancel-button {
  background: #f0f2f5;
  color: #666;
  padding: 12px 24px;
  border-radius: 25px;
  border: none;
  cursor: pointer;
}

/* AI侧边栏 */
.ai-sidebar {
  width: 0;
  height: calc(100vh - 100px); /* 保持与激活状态相同的高度计算 */
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
/* 响应式设计 */
@media (max-width: 768px) {
  .question-container {
    flex-direction: column;
    margin: 8px;
    height: auto;
  }

  .ai-sidebar.active {
    width: 100%;
    height: 50vh;
    position: relative;
    top: 0;
  }
}
.submit-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #6c42b5, #8a63d2);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 4px rgba(108, 66, 181, 0.2);
}
.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(108, 66, 181, 0.3);
}
.submit-button:disabled {
  background: #e0e4e9;
  color: #a0a4a9;
  cursor: not-allowed;
  opacity: 0.8;
}
.reset-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #f0f2f5, #e4e6e9);
  color: #666;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.reset-button:hover {
  background: linear-gradient(135deg, #e4e6e9, #d8dadd);
}
.fill-blank-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin: 24px 0;
}

.blank-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.blank-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e4e9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  min-width: 280px;
  resize: vertical; /* 允许垂直调整大小 */
  white-space: pre-wrap; /* 保留换行符 */
  word-break: break-word; /* 允许单词换行 */
  min-height: 44px; /* 保持与原输入框高度一致 */
}

.blank-input:focus {
  border-color: #8a63d2;
  outline: none;
  box-shadow: 0 0 0 3px rgba(108, 66, 181, 0.1);
}

.blank-input:disabled {
  background-color: #f8f9fa;
  border-color: #e9ecef;
}

.correct-answer {
  color: #10b981;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

/* 错误状态提示（在提交后显示） */
.blank-input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .blank-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .blank-input {
    width: 100%;
    min-width: auto;
  }
}
/* 添加新的样式规则 */
.option-item.correct {
  border-color: #10b981 !important;
  background-color: #f0fdf4;
}

.option-item.incorrect {
  border-color: #ef4444 !important;
  background-color: #fef2f2;
}

.blank-input.correct {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.blank-input.incorrect {
  border-color: #ef4444;
  background-color: #fef2f2;
}

/* 调整原有选中样式优先级 */
.option-item.selected {
  border-color: #6c42b5;
  background: #f8f5ff;
}
.markdown-content {
  font-family: 'Inter', sans-serif;
  line-height: 1.8;
  overflow-x: hidden;
}

.markdown-content h2 {
  color: #2c3e50;
  margin-top: 1.5em;
}

.markdown-content pre {
  background: #f8f9ff;
  padding: 1rem;
  border-radius: 8px;
  overflow-y: auto;
}

.markdown-content code {
  font-family: 'Fira Code', monospace;
  background: #f8f9ff;
  padding: 2px 6px;
  border-radius: 4px;
}
/* 新增删除按钮样式 */
.delete-button {
  background: linear-gradient(135deg, #ff6b6b, #ff4757);
  color: white;
  margin-left: 8px;
}

.delete-button:hover {
  background: linear-gradient(135deg, #ff5252, #ff3d4f);
}
</style>