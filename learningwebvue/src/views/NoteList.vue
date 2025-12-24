<template>
  <div class="study-note-list-container">
    <header class="page-header">
      <h1 class="page-title">📚 学习笔记</h1>
      <div class="decorative-line"></div>
    </header>

    <div class="content-wrapper">
      <transition name="fade" mode="out-in">
        <div v-if="loading" class="loading-wrapper">
          <div class="progress-bar">
            <div class="progress"></div>
          </div>
        </div>

        <div v-else-if="notes.length === 0" class="empty-state">
          <p>暂时没有找到笔记</p>
          <p>请检查网络或稍后再试</p>
        </div>

        <div v-else class="notes-grid">
          <StudyNoteItem
              v-for="note in notes"
              :key="note.note_id"
              :study-note="note"
              @select-note="handleSelectNote"
              class="note-card"
          />
        </div>
      </transition>

      <button v-if="!loading" class="floating-add-button" @click="showForm = true">+</button>
    </div>

    <!-- 添加笔记表单模态框 -->
    <div v-if="showForm" class="modal-overlay">
      <div class="modal-content">
        <h2>添加新笔记</h2>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>笔记名称:</label>
            <input v-model="newNote.note_name" required>
          </div>
          <div class="form-group">
            <label>用户ID:</label>
            <input v-model="newNote.user_id" type="number" required>
          </div>
          <div class="form-group">
            <label>封面图标:</label>
            <div class="file-upload-wrapper">
              <input
                  type="file"
                  @change="handleFileUpload"
                  accept="image/*"
                  required
              >
            </div>
          </div>
          <div class="form-actions">
            <button type="button" @click="cancelForm">取消</button>
            <button type="submit">创建笔记</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import StudyNoteItem from '../components/StudyNoteItem.vue'

export default {
  components: { StudyNoteItem },
  setup() {
    const router = useRouter()
    const notes = ref([])
    const loading = ref(true)
    const showForm = ref(false)
    const newNote = ref({
      note_name: '',
      user_id: null,
      icon: null
    })

    const fetchNotes = async () => {
      const user_id = 1
      const url = `http://127.0.0.1:8000/users/getNotesById?user_id=${user_id}`
      try {
        loading.value = true
        const response = await fetch(url)
        if (!response.ok) throw new Error(`HTTP错误 ${response.status}`)

        const { data } = await response.json()
        console.log(data)
        notes.value = data.map(note => ({
          ...note,
          // 确保字段名称匹配
          note_id: note.note_id,
          note_name: note.note_name,
          created_at: note.created_at,
          icon: note.icon
        }))
        console.log(notes)
      } catch (error) {
        console.error('获取笔记失败:', error)
        notes.value = []
      } finally {
        loading.value = false
      }
    }

    const handleSelectNote = (noteId) => {
      router.push(`/note/${noteId}`)
    }

    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        newNote.value.icon = file
      }
    }

    const cancelForm = () => {
      showForm.value = false
      newNote.value = {
        note_name: '',
        user_id: null,
        icon: null
      }
    }

    const handleSubmit = async () => {
      const formData = new FormData()
      formData.append('note_name', newNote.value.note_name)
      formData.append('user_id', newNote.value.user_id)
      formData.append('icon', newNote.value.icon)

      try {
        const response = await fetch('http://127.0.0.1:8000/users/addNote', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) throw new Error('创建笔记失败')

        await fetchNotes() // 刷新列表
        cancelForm()
      } catch (error) {
        console.error('创建失败:', error)
        alert('创建失败，请稍后重试')
      }
    }

    onMounted(fetchNotes)

    return {
      notes,
      loading,
      handleSelectNote,
      showForm,
      newNote,
      handleFileUpload,
      handleSubmit,
      cancelForm
    }
  }
}
</script>

<style scoped>
/* 完整样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', 'Helvetica Neue', system-ui, sans-serif;
}

.study-note-list-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  background: linear-gradient(to bottom right, #f8f9fa 0%, #f1f3f5 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.page-title {
  font-size: 2.5rem;
  color: #2b2d42;
  letter-spacing: -0.05em;
  margin-bottom: 1.2rem;
  font-weight: 700;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}

.decorative-line {
  width: 120px;
  height: 4px;
  background: linear-gradient(90deg, #8d99ae 0%, #ef233c 100%);
  margin: 0 auto;
  border-radius: 2px;
  transform: skewX(-15deg);
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  padding: 1.5rem 0;
  position: relative;
}

.loading-wrapper {
  padding: 4rem 0;
  display: flex;
  justify-content: center;
}

.progress-bar {
  width: 300px;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress {
  width: 45%;
  height: 100%;
  background: linear-gradient(90deg, #4cc9f0 0%, #3a0ca3 100%);
  border-radius: 4px;
  animation: shimmer 2.4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

.empty-state {
  text-align: center;
  padding: 4rem 0;
  color: #6c757d;
}

.empty-state p {
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.floating-add-button {
  position: fixed;
  bottom: 2.5rem;
  right: 2.5rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #3a86ff;
  color: white;
  font-size: 2rem;
  border: none;
  box-shadow: 0 6px 16px rgba(58,134,255,0.25);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.floating-add-button:hover {
  transform: scale(1.1) rotate(90deg);
  background: #2563eb;
  box-shadow: 0 8px 24px rgba(58,134,255,0.35);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 12px 32px rgba(0,0,0,0.15);
  transform: translateY(-20px);
  animation: modalEnter 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes shimmer {
  0% { transform: translateX(-150%) skewX(-20deg); }
  100% { transform: translateX(250%) skewX(-20deg); }
}

@keyframes modalEnter {
  to { transform: translateY(0); opacity: 1; }
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  color: #4a4e69;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #3a86ff;
  box-shadow: 0 0 0 3px rgba(58,134,255,0.15);
}

.file-upload-wrapper input[type="file"] {
  border: 2px dashed #ced4da;
  padding: 1rem;
  width: 100%;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.file-upload-wrapper input[type="file"]:hover {
  border-color: #3a86ff;
  background: #f8f9ff;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.form-actions button {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.form-actions button[type="submit"] {
  background: #3a86ff;
  color: white;
}

.form-actions button[type="submit"]:hover {
  background: #2563eb;
}

.form-actions button[type="button"] {
  background: #e9ecef;
  color: #495057;
}

.form-actions button[type="button"]:hover {
  background: #dee2e6;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>