<template>
  <div class="chat-container">
    <!-- 新增 Temperature 设置工具栏 -->
    <div class="config-toolbar">
      <label for="temperature-select">Temperature 设置：</label>
      <select
          id="temperature-select"
          v-model="temperature"
          class="temperature-select"
      >
        <option
            v-for="(desc, value) in temperatureOptions"
            :key="value"
            :value="Number(value)"
        >
          {{ desc }} ({{ value }})
        </option>
      </select>
    </div>
    <div class="messages-panel" ref="messagesPanel">
      <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message-bubble', message.role]"
      >
        <MarkdownRenderer
            v-if="message.role !== 'system'"
            :content="message.content"
            class="message-content"
        />
      </div>
      <div ref="messagesEnd"></div>
    </div>

    <div class="input-area">
      <textarea
          v-model="inputText"
          @keydown.enter.prevent="handleEnter"
          placeholder="输入消息..."
      ></textarea>
      <button @click="sendMessage" :disabled="!hasInputText">
        发送
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import _ from 'lodash'
import MarkdownRenderer from "@/components/MarkdownRenderer.vue";
const temperatureOptions = {
  '0.0': '代码生成/数学解题',
  '1.0': '数据抽取/分析',
  '1.3': '通用对话/翻译',
  '1.5': '创意类写作/诗歌创作'
}
const temperature = ref(1.0)
const props = defineProps({
  messages: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['send'])

const inputText = ref('')
const messagesPanel = ref(null)
let isUserScrolled = false

const checkScrollPosition = () => {
  if (!messagesPanel.value) return
  const { scrollTop, scrollHeight, clientHeight } = messagesPanel.value
  isUserScrolled = scrollTop + clientHeight < scrollHeight - 50
}

const scrollToBottom = _.throttle(() => {
  if (!messagesPanel.value || isUserScrolled) return

  requestAnimationFrame(() => {
    messagesPanel.value.scrollTo({
      top: messagesPanel.value.scrollHeight,
      behavior: 'smooth'
    })
  })
}, 300)

watch(() => props.messages, async () => {
  await nextTick()
  scrollToBottom()
}, { deep: true })

onMounted(() => {
  messagesPanel.value?.addEventListener('scroll', checkScrollPosition)
})

onUnmounted(() => {
  messagesPanel.value?.removeEventListener('scroll', checkScrollPosition)
})

const hasInputText = computed(() => inputText.value.trim().length > 0)

const sendMessage = () => {
  if (!hasInputText.value) return
  emit('send', {content:inputText.value.trim(),
  temperature:temperature.value})
  inputText.value = ''
}

const handleEnter = (e) => {
  if (e.shiftKey) {
    inputText.value += '\n'
  } else {
    sendMessage()
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: sticky;
  top: 20px;
  bottom: 20px;
  max-height: calc(100vh - 40px);
}

.messages-panel {
  height: 70vh;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  contain: strict;
  transform: translateZ(0);
  will-change: scroll-position;
}

.messages-panel::-webkit-scrollbar {
  width: 8px;
}

.messages-panel::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.messages-panel::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.messages-panel::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.message-bubble {
  margin: 8px 0;
  transition: transform 0.2s ease;
  width: fit-content;
}

.message-bubble:hover {
  transform: translateX(4px);
}

.message-bubble.assistant {
  align-self: flex-start;
}

.message-bubble.user {
  align-self: flex-end;
}

.message-content {
  padding: 14px 18px;
  border-radius: 14px;
  font-size: 15px;
  line-height: 1.7;
  box-shadow: 0 3px 12px rgba(0,0,0,0.03);
  font-family: 'Inter', system-ui, sans-serif;
  color: #1f2937;
}

.message-bubble.user .message-content {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 18px 18px 4px 18px;
}

.message-bubble.assistant .message-content {
  background: linear-gradient(145deg, #ffffff, #f8fafc);
  border: 1px solid #e2e8f0;
  border-radius: 18px 18px 18px 4px;
}

.input-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 10px;
}

textarea {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: vertical;
  min-height: 50px;
  font-family: inherit;
}

button {
  padding: 12px 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  font-weight: 500;
  transition: transform 0.2s ease;
  min-width: 80px;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

@media (max-width: 768px) {
  .message-bubble {
    max-width: 90%;
  }

  textarea {
    font-size: 14px;
  }
}
.config-toolbar {
 padding: 12px 20px;
 background: #f8f9fa;
 border-bottom: 1px solid #e9ecef;
 display: flex;
 align-items: center;
 gap: 12px;
}

.temperature-select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #ced4da;
  background: white;
  font-size: 14px;
  width: 260px;
  transition: border-color 0.2s ease;
}

.temperature-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .config-toolbar {
    flex-direction: column;
    align-items: stretch;
    padding: 12px;
  }

  .temperature-select {
    width: 100%;
  }
}
</style>