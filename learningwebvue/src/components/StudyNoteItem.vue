<template>
  <div class="study-note-card" v-if="studyNote" @mouseenter="isHovered = true" @mouseleave="isHovered = false">
    <div class="cover-wrapper">
      <div class="cover-placeholder">
        <img
            v-if="studyNote?.icon"
            :src="studyNote.icon"
            :alt="studyNote.note_name"
            class="note-icon"
            @error="handleImageError"
        >
        <svg
            v-else
            class="note-icon placeholder"
            viewBox="0 0 24 24"
            aria-hidden="true"
        >
          <path
              fill="currentColor"
              d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z"
          />
        </svg>
      </div>
      <div class="shine-effect" :class="{ active: isHovered }"></div>
    </div>

    <div class="content">
      <h3 class="title">{{ studyNote.note_name }}</h3>
      <div class="meta-info">
        <svg class="time-icon" viewBox="0 0 24 24">
          <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm-.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
        </svg>
        <p class="created-at">{{ formatDate(studyNote.created_at) }}</p>
      </div>
    </div>

    <button @click="handleClick" class="action-button">
      <span>查看笔记</span>
      <div class="arrow-wrapper">
        <svg class="arrow-icon" viewBox="0 0 24 24">
          <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
        </svg>
      </div>
    </button>
  </div>

  <div class="error-card" v-else>
    <div class="error-icon">📖</div>
    <p class="error-message">内容暂时不可用</p>
    <p class="error-sub">请稍后重试</p>
  </div>
</template>

<script>
export default {
  name: 'StudyNoteCard',
  props: {
    studyNote: {
      type: Object,
      required: true,
      default: () => ({
        note_id: null,
        note_name: '未命名笔记',
        user_id: null,
        created_at: new Date().toISOString(),
        icon: null
      }),
      validator: (value) => {
        return 'note_id' in value && 'note_name' in value
      }
    }
  },
  data() {
    return {
      isHovered: false
    }
  },
  methods: {
    handleClick() {
      if (this.studyNote?.note_id) {
        this.$emit('select-note', this.studyNote.note_id)
      }
    },
    formatDate(isoString) {
      if (!isoString) return '未知日期'
      try {
        const date = new Date(isoString)
        return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
      } catch {
        return '日期格式错误'
      }
    }
  }
}
</script>

<style scoped>
.study-note-card {
  background: white;
  border-radius: 16px;
  padding: 1.8rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 1.2rem;
}

.study-note-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
}

.cover-wrapper {
  position: relative;
  height: 160px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f0f4ff 0%, #f8f9fa 100%);
  display: grid;
  place-items: center;
}

.note-icon {
  height: 160px;
  fill: #c0d6e8;
}

.shine-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(
      90deg,
      rgba(255,255,255,0) 0%,
      rgba(255,255,255,0.3) 50%,
      rgba(255,255,255,0) 100%
  );
  transition: all 0.8s ease;
  opacity: 0;
}

.shine-effect.active {
  opacity: 1;
  left: 140%;
}

.title {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
  letter-spacing: -0.3px;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 0.8rem;
}

.time-icon {
  width: 18px;
  height: 18px;
  fill: #6c757d;
}

.created-at {
  color: #6c757d;
  font-size: 0.95rem;
  margin: 0;
  opacity: 0.9;
}

.action-button {
  background: linear-gradient(135deg, #42b983 0%, #33a06f 100%);
  color: white;
  border: none;
  padding: 0.9rem 1.6rem;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-button span {
  position: relative;
  z-index: 1;
}

.action-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
  transition: all 0.6s ease;
}

.action-button:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(66, 185, 131, 0.3);
}

.action-button:hover::before {
  left: 140%;
}

.arrow-wrapper {
  transition: transform 0.3s ease;
}

.action-button:hover .arrow-wrapper {
  transform: translateX(3px);
}

.arrow-icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.error-card {
  background: #fff9f2;
  border: 2px dashed #ffd8b2;
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.error-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  opacity: 0.8;
  animation: float 3s ease-in-out infinite;
}

.error-message {
  color: #ff9100;
  font-weight: 500;
  margin: 0.5rem 0;
}

.error-sub {
  color: #ff9100;
  opacity: 0.7;
  font-size: 0.9rem;
  margin: 0;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}
</style>