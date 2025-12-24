<template>
  <div class="page-container">
    <div class="catalog-panel">
      <div class="search-box">
        <input
            v-model="keyword"
            type="text"
            placeholder="输入目录名称搜索"
            class="search-input"
        >
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        加载中...
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="error-state">
        {{ error }}
        <button @click="loadChapter">重试</button>
      </div>

      <div v-else class="catalog-list">
        <div
            v-for="(item, index) in filteredCatalogs"
            :key="item.id"
            :class="['catalog-item', { 'active': activeIndex === index }]"
            @click="handleClick(index, item)"
        >
          {{ item.chapter_name }}
        </div>

        <!-- 新增目录区域 -->
        <div v-if="showAddInput" class="add-input-container">
          <input
              ref="addInput"
              v-model="newCatalogName"
              type="text"
              placeholder="输入新目录名称"
              class="add-input"
              @keyup.enter="confirmAdd"
              @keyup.esc="cancelAdd"
          >
          <div class="action-buttons">
            <button class="confirm-btn" @click="confirmAdd">确定</button>
            <button class="cancel-btn" @click="cancelAdd">取消</button>
          </div>
        </div>

        <div
            v-else
            class="add-button"
            @click="startAddCatalog"
        >
          <span class="plus-symbol-catalog">+</span>
          <span class="button-text">新建目录</span>
        </div>
      </div>
    </div>
    <div class="main-content-wrapper">
      <div
          v-for="(item, index) in knowledges"
          :key="item.id"
      >
        <KnowledgePoint
            :title="item.title"
            :content="item.content"
            :personal-understanding="item.personalUnderstanding"
            :study-count="item.studyCount"
            :chat-history="item.chatHistory"
            @submit="(knowledgeNeedId) => handleSubmitKnowledge(knowledgeNeedId, item)"
            @study-complete="()=>handleStudyComplete(item)"
            @chat-message="(msg) => handleChatMessage(msg, item)"
        />
      </div>
      <div
          class="add-knowledge-button"
          @click="startAddKnowledge"
      >
        <span class="plus-symbol-knowledge">+添加知识点</span>
      </div>
      <div
        v-for="(item, index) in currentQuestion"
        :key="item.id"
        >
        <question-component
            :questionData="item"
            :chatHistory="item.chatHistory"
            @answer-submitted="(result) => handleAnswer(result, item)"
            @update-note="(newQuestionNote)=>handleQuestionNoteUpdate(newQuestionNote, item)"
            @update-content="(newQuestionContent)=>handleQuestionContentUpdate(newQuestionContent, item)"
            @add-users-answer = "(answer) => addAnswerToChathistory(answer, item)"
            @chat-message="(msg) => handleChatMessage(msg, item)"
            @delete="handleDeleteQuestion(item)"
        />
      </div>
      <div
          class="add-question-button"
          @click="createQuestion('single_choice')"
      >
        <span class="plus-symbol-question">+添加单选题</span>
      </div>
      <div
          class="add-question-button"
          @click="createQuestion('multiple_choice')"
      >
        <span class="plus-symbol-question">+添加多选题</span>
      </div>
      <div
          class="add-question-button"
          @click="createQuestion('fill_blank')"
      >
        <span class="plus-symbol-question">+添加填空题</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, nextTick, toRaw} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import KnowledgePoint from "@/components/KnowledgePoint.vue";
import ChatWindow from "@/components/ChatComponent.vue";
import QuestionComponent from "@/components/QuestionComponent.vue";

const route = useRoute()
const router = useRouter()

// 响应式状态
const noteId = ref('')
const catalogs = ref([])
const isLoading = ref(false)
const error = ref(null)
const keyword = ref('')
const activeIndex = ref(-1)
const showAddInput = ref(false)
const newCatalogName = ref('')
const addInput = ref(null)
const activeChapterId = ref(-1)
const currentQuestion = ref([])
// 创建题目
const createQuestion = (type)=> {
  const templateMap = {
    single_choice: {
      content: JSON.stringify({
        stem: '',
        type: 'single_choice',
        options: [
          {key: 'A', value: ''},
          {key: 'B', value: ''},
          {key: 'C', value: ''},
          {key: 'D', value: ''},
        ],
        answer: '',
        explanation: ''
      }),
      personal_note: '',
      correct_count: 0,
      wrong_count: 0,
    },
    multiple_choice: {
      content: JSON.stringify({
        stem: '',
        type: 'multiple_choice',
        options: [
          {key: 'A', value: ''},
          {key: 'B', value: ''},
          {key: 'C', value: ''},
          {key: 'D', value: ''},
        ],
        answer: [],
        explanation: ''
      }),
      personal_note: '',
      correct_count: 0,
      wrong_count: 0,
    },
    fill_blank: {
      content: JSON.stringify({
        stem: '',
        type: 'fill_blank',
        blanks: [
          {answer: ''},
        ],
        explanation: ''
      }),
      personal_note: '',
      correct_count: 0,
      wrong_count: 0,
    }
  };
  const newQuestion = {
    ...templateMap[type],
  };
  console.log(newQuestion)
  const url = `http://127.0.0.1:8000/users/addQuestion?chapter_id=${activeChapterId.value}`;

  // 发送更新请求到服务器
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newQuestion),
  })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();

      }).then(data =>{
        currentQuestion.value.push(data.data)
        console.log(currentQuestion)
      })
      .catch(error => {
        console.error('更新失败:', error);
      });
}
// 处理答案提交的逻辑
const handleAnswer = (result, item) => {
  // 先更新本地数据（乐观更新）
  const wasCorrect = result.isCorrect;
  if (wasCorrect) {
    item.correct_count++;
  } else {
    item.wrong_count++;
  }
  const url = 'http://127.0.0.1:8000/users/updateQuestion';
  item.personal_note += item.answer+"\n";
  // 发送更新请求到服务器
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item),
  })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(updatedItem => {
        item.correct_count = updatedItem.data.correct_count;
        item.wrong_count = updatedItem.data.wrong_count;
      })
      .catch(error => {
        console.error('更新失败:', error);

        // 回滚本地修改
        if (wasCorrect) {
          item.correct_count--;
        } else {
          item.wrong_count--;
        }
      });
};
const addAnswerToChathistory = (answer, thisItem)=>{
  thisItem.chatHistory.forEach((message, index) => {
    // 2. 解构获取 role 和 content
    const { role, content } = message;
    if (role === 'system') {
      message.content += "\n用户的回答如下"+answer+"\n\n请根据用户的回答来分析问题"; // 修改系统消息
      thisItem.answer = "第"+(thisItem.wrong_count+thisItem.correct_count+1).toString(10)+"次回答："+answer;
    }
  });
}
const handleDeleteQuestion = async (item) => {
  try {
    // 验证参数有效性
    if (!item?.question_id) {
      alert('无效的题目ID');
      return;
    }
    console.log('questionId:',item.question_id)
    // 发送删除请求
    const response = await fetch(`http://127.0.0.1:8000/users/deleteQuestion?questionId=${item.question_id}`, {
      method: 'DELETE',
    });

    // 处理HTTP错误状态
    if (!response.ok) {
      const errorResult = await response.json();
      throw new Error(errorResult.message || `HTTP错误！状态码：${response.status}`);
    }

    // 处理成功响应（即使后台没有返回数据）
    const result = await response.json();

    for (let i = currentQuestion.value.length - 1; i >= 0; i--) {
      if (currentQuestion.value[i] === item) {
        currentQuestion.value.splice(i, 1);
      }
    }

    // 可选：添加成功反馈
    console.log('删除成功:', result);

  } catch (error) {
    // 统一错误处理
    console.error('删除操作失败:', error);

    // 更友好的错误提示
    const errorMessage = error.message.includes('HTTP错误')
        ? `服务器错误（${error.message}）`
        : `网络连接异常，请检查网络后重试`;

    alert(`删除失败: ${errorMessage}`);

    // 可选：执行错误恢复操作，如回滚本地状态
  }
};
//处理更新问题笔记之后的逻辑
const handleQuestionNoteUpdate = (newQuestionNote,item)=> {
  console.log('更新笔记:', newQuestionNote);
  const old_personal_note = item.personal_note
  item.personal_note = newQuestionNote;
  const url = 'http://127.0.0.1:8000/users/updateQuestion';

  // 发送更新请求到服务器
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item),
  })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(updatedItem => {
        item.personal_note = updatedItem.data.personal_note;
        item.chatHistory = [{'role':"system", 'content':"这个问题的内容如下所示:\n\n"+item.content+"\n\n"+"我对于该问题的理解是:\n\n"
              +item.personal_note+"\n\n你需要帮助理解这个问题，" +
              "用户需要完全搞明白这个问题，你需要解释用户的理解是否正确，向用户阐明用户的错误之处。\n\n" +
              "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"}]
      })
      .catch(error => {
        console.error('更新失败:', error);
        item.personal_note = old_personal_note
      });
}
const handleQuestionContentUpdate = (newQuestionContent,item)=> {
  console.log('更新笔记:', newQuestionContent);
  const old_Content = item.content
  item.content = newQuestionContent;
  const url = 'http://127.0.0.1:8000/users/updateQuestion';
  console.log("更新后的信息：",item)
  // 发送更新请求到服务器
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item),
  })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(updatedItem => {
        item.content = updatedItem.data.content;
        item.chatHistory = [{'role':"system", 'content':"这个问题的内容如下所示:\n\n"+item.content+"\n\n"+"我对于该问题的理解是:\n\n"
              +item.personal_note+"\n\n你需要帮助理解这个问题，" +
              "用户需要完全搞明白这个问题，你需要解释用户的理解是否正确，向用户阐明用户的错误之处。\n\n" +
              "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"}]
      })
      .catch(error => {
        console.error('更新失败:', error);
        item.content = old_Content
      });
}
// 初始化
onMounted(async () => {
  try {
    noteId.value = route.params.noteId
    await loadChapter()
    // 等待数据和 DOM 更新
    await nextTick()

    // 自动点击第一条
    if (filteredCatalogs.value.length > 0) {
      handleClick(0, filteredCatalogs.value[0])
    }
  } catch (err) {
    console.error('初始化错误:', err)
  }
})

// 获取目录数据
const loadChapter = async () => {
  try {
    isLoading.value = true
    error.value = null
    const url = `http://127.0.0.1:8000/users/getChaptersByNoteId?note_id=${noteId.value}`
    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    catalogs.value = data.data
  } catch (err) {
    error.value = `加载失败: ${err.message}`
    console.error('加载目录失败:', err)
  } finally {
    isLoading.value = false
  }
}
// 过滤目录
const filteredCatalogs = computed(() => {
  const searchTerm = keyword.value.toLowerCase()
  return catalogs.value.filter(item =>
      item.chapter_name.toLowerCase().includes(searchTerm)
  )
})
//处理目录被按下的情形
const handleClick = (index, catalog) => {
  activeIndex.value = index
  activeChapterId.value = catalog.chapter_id
  loadKnowledge(catalog)
  loadQuestion(catalog)
}
// 加载数据
const loadKnowledge= async(catalog) => {
  try {
    isLoading.value = true
    error.value = null
    const url = `http://127.0.0.1:8000/users/getKnowledgeByNoteId?chapter_id=${catalog.chapter_id}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    knowledges.value = data.data.map(item => ({
      ...item,
      chatHistory: [{'role':"system", 'content':"这个知识点的内容如下所示:\n\n"+item.content+"\n\n"+"我对于该知识点的理解是:\n\n"
            +item.personalUnderstanding+"\n\n你需要帮助理解这个知识点，但是用户" +
            "不一定问这个知识点的内容，当用户不问此知识点的内容的时候，就不需要考虑此知识点了，请记住这条规则。\n\n" +
            "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"}]   // 新增字段
    }));
  } catch (err) {
    error.value = `加载失败: ${err.message}`
    console.error('加载目录失败:', err)
  } finally {
    isLoading.value = false
  }
}
// 加载问题数据
const loadQuestion= async(catalog) => {
  try {
    isLoading.value = true
    error.value = null
    const url = `http://127.0.0.1:8000/users/getQuestionByNoteId?chapter_id=${catalog.chapter_id}`
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    console.log(data)
// 处理接口返回的 data.data
    currentQuestion.value = data.data.map(item => ({
      ...item,
      question_id: item.question_id,
      // 强制将 content 序列化为格式化后的 JSON 字符串
      content: JSON.stringify(item.content),
      // 添加 chatHistory（使用已序列化的 content）
      chatHistory: [{
        role: "system",
        content: "这个问题的内容如下所示:\n\n"+JSON.stringify(item.content, null, 2)+"\n\n"+"我对于该问题的理解是:\n\n"
              +item.personal_note+"\n\n你需要帮助理解这个问题，" +
              "用户需要完全搞明白这个问题，你需要解释用户的理解是否正确，向用户阐明用户的错误之处。\n\n" +
              "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"
      }]
    }));
    console.log(currentQuestion)
  } catch (err) {
    error.value = `加载失败: ${err.message}`
    console.error('加载目录失败:', err)
  } finally {
    isLoading.value = false
  }
}
const startAddCatalog = async () => {
  showAddInput.value = true
  await nextTick()
  addInput.value.focus()
}
// 添加一个新的知识点
const startAddKnowledge = async () =>{
  const updateData = {
    title: '',
    content: '',
    personalUnderstanding: '',
    studyCount: 0,
    chatHistory: [{'role':"system", 'content':"这个知识点的内容如下所示:\n\n"+""+"\n\n"+"我对于该知识点的理解是:\n\n"
          +""+"\n\n你需要帮助理解这个知识点，但是用户" +
          "不一定问这个知识点的内容，当用户不问此知识点的内容的时候，就不需要考虑此知识点了，请记住这条规则。\n\n" +
          "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"}]   // 新增字段
  };
  try {
    const url = `http://127.0.0.1:8000/users/addKnowledgeByChapterId?chapter_id=${activeChapterId.value}`
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updateData)
    });

    if (!response.ok) throw new Error(`HTTP 错误! 状态码: ${response.status}`);

    const data = await response.json();
    knowledges.value.push(data.data)
  } catch (error) {
    console.error('更新失败:', error);
  }
  knowledges.value.push(
      updateData
  )
}
const confirmAdd = async () => {  // 改为异步函数
  const chapterName = newCatalogName.value?.trim()  // 修复.value的访问方式
  if (chapterName) {
    try {
      // 提交到后端
      const response = await fetch(
          `http://127.0.0.1:8000/users/addChapterByNoteId`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ chapter_name: chapterName,note_id:noteId.value })
          }
      )

      if (!response.ok) throw new Error('提交失败')

      // 添加成功后的本地更新
      catalogs.value.push({
        chapter_id: Date.now(), // 临时ID，实际应从响应获取
        chapter_name: chapterName,
        summary: '',
        level: 1
      })
    } catch (err) {
      console.error('提交错误:', err)
      alert('保存失败，请重试')
      return // 失败时保持输入状态
    }
  }

  cancelAdd() // 仅在成功时清除
}

const cancelAdd = () => {
  showAddInput.value = false
  newCatalogName.value = ''
}
//下面是知识点相关的数据结构
const knowledges = ref([]); // 正确变量名为 knowledges

// 提交处理
const handleSubmitKnowledge = async (updateData, knowledgeItem) => {
  try {
    // 构建请求数据（避免直接修改原对象，先创建新对象）
    const updatedItem = {
      ...updateData,
      studyCount: knowledgeItem.studyCount, // 保留原有或更新，根据实际需求
      point_id: knowledgeItem.point_id
    };
    console.log(updateData)
    const response = await fetch('http://127.0.0.1:8000/users/updateKnowledgeByPointId', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedItem)
    });

    if (!response.ok) throw new Error(`HTTP 错误! 状态码: ${response.status}`);

    const data = await response.json();
    console.log("返回的数据",data.data)
    console.log('更新前:',knowledges)
    // 修改后的更新逻辑
    const index = knowledges.value.findIndex(item => item.id === knowledgeItem.id); // 修复变量名拼写错误
    if (index !== -1) {
      // 创建新对象确保触发响应式更新
      const newItem = {
        ...knowledges.value[index],  // 保留未修改的字段
        ...data.data, // 用接口返回的最新数据覆盖
        chatHistory: [{'role':"system", 'content':"这个知识点的内容如下所示:\n\n"+data.data.content+"\n\n"+"我对于该知识点的理解是:\n\n"
              +data.data.personalUnderstanding+"\n\n你需要帮助理解这个知识点，但是用户" +
              "不一定问这个知识点的内容，当用户不问此知识点的内容的时候，就不需要考虑此知识点了，请记住这条规则。\n\n" +
              "另外永远记住，生成答案的时候按照标准的markdown文档和katex公式进行生成"}]
      };

      // 正确使用 splice 触发响应式更新
      knowledges.value.splice(index, 1, newItem); // 修复变量名拼写错误
    }
    console.log('更新后:',knowledges)
  } catch (error) {
    console.error('更新失败:', error);
  }
};
// 学习完成处理
const handleStudyComplete = async (knowledgeItem) => {
  knowledgeItem.studyCount += 1;
  try {
    const response = await fetch('http://127.0.0.1:8000/users/updateKnowledgeByPointId', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(knowledgeItem)
    });

    if (!response.ok) throw new Error(`HTTP 错误! 状态码: ${response.status}`);

    const data = await response.json();
    console.log("返回的数据",data.data)
    console.log('更新前:',knowledges)
    // 修改后的更新逻辑
    const index = knowledges.value.findIndex(item => item.id === knowledgeItem.id); // 修复变量名拼写错误
    if (index !== -1) {
      // 创建新对象确保触发响应式更新
      const newItem = {
        ...knowledges.value[index],  // 保留未修改的字段
        ...data.data
      };

      // 正确使用 splice 触发响应式更新
      knowledges.value.splice(index, 1, newItem); // 修复变量名拼写错误
    }
    console.log('更新后:',knowledges)
  } catch (error) {
    console.error('更新失败:', error);
  }
};
// 处理AI消息
const handleChatMessage = async (message, thisKnowledge) => {
  console.log(thisKnowledge.chatHistory)
  thisKnowledge.chatHistory.push({
    role: 'user',
    content: message.content,
  });
  try {
    const url = `http://127.0.0.1:8000/users/aiTalkKnowledge?temperature=${message.temperature}`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      },
      body: JSON.stringify(thisKnowledge.chatHistory)
    })

    // 获取流阅读器
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    // 添加临时助手消息
    thisKnowledge.chatHistory.push({
      role: 'assistant',
      content: '',
      isLoading: true
    })
    // 获取最后一条消息的索引
    const lastIndex = thisKnowledge.chatHistory.length - 1

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      // 更新最后一条消息内容
      const chunk = decoder.decode(value)
      thisKnowledge.chatHistory[lastIndex].content += chunk

      // 强制触发Vue响应式更新（两种方式任选其一）
      // 方式1：使用数组解构
      // chatHistory.value = [...chatHistory.value]

      // 方式2：使用Vue的响应式API
      // import { triggerRef } from 'vue'
      // triggerRef(chatHistory)
    }

    // 流结束时更新状态
    thisKnowledge.chatHistory[lastIndex].isLoading = false

  } catch (error) {
    // 错误处理：移除临时消息并显示错误
    thisKnowledge.chatHistory.splice(-1, 1)
    console.error('请求失败:', error)
    // 可以添加错误消息
    thisKnowledge.chatHistory.push({
      role: 'system',
      content: `错误: ${error.message}`,
      isError: true
    })
  }
};
</script>

<style scoped>
.page-container {
  display: flex;
  height: 100vh;
  background: #fff;
  overflow: hidden; /* 新增：防止整个页面滚动 */
}

.catalog-panel {
  flex: 0 0 280px; /* 固定宽度 */
  background: #fafafa;
  border-right: 1px solid #e8e8e8;
  overflow-y: auto;
  height: 100vh; /* 新增：固定高度 */
  display: flex; /* 新增：弹性布局 */
  flex-direction: column; /* 新增：垂直排列 */
}

.search-box {
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.search-input {
  width: 90%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.catalog-list {
  height: calc(100vh - 72px);
  overflow-y: auto;
  padding: 0 16px;
  flex: 1; /* 新增：撑满剩余空间 */
}

.catalog-item {
  padding: 12px;
  margin: 8px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
}

.catalog-item:hover {
  background: #f0f7ff;
}

.catalog-item.active {
  background: #e6f4ff;
  color: #1677ff;
  font-weight: 500;
}

.add-button {
  display: flex;
  align-items: center;
  padding: 12px;
  margin: 16px 0;
  color: #1677ff;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.add-button:hover {
  background: #f0f7ff;
}

.plus-symbol-catalog {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: 8px;
  font-size: 18px;
  line-height: 1;
}
.plus-symbol-knowledge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 20px;
  margin-right: 8px;
  font-size: 18px;
  line-height: 1;
}
.plus-symbol-question {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 20px;
  margin-right: 8px;
  font-size: 18px;
  line-height: 1;
}

.add-input-container {
  margin: 16px 0;
  padding: 8px;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
}

.add-input {
  width: 90%;
  padding: 8px;
  margin-bottom: 8px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  font-size: 14px;
}

.add-input:focus {
  outline: none;
  border-color: #1890ff;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.confirm-btn {
  padding: 4px 12px;
  background: #1677ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-btn:hover {
  background: #0958d9;
}

.cancel-btn {
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #d9d9d9;
  color: rgba(0, 0, 0, 0.85);
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:hover {
  border-color: #1677ff;
  color: #1677ff;
}

.main-content-wrapper {
  flex: 1;
  min-width: 0; /* 允许内容压缩 */
  display: flex;
  flex-direction: column;
  background: #f5f7fb;
  overflow-y: auto; /* 新增：允许内容区域独立滚动 */
}
.add-knowledge-button {
  /* 布局 */
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  flex-shrink: 0; /* 禁止高度压缩 */
  /* 视觉样式 */
  background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
  border-radius: 8px;
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  /* 文字样式 */
  color: white;
  font-family: 'Segoe UI', sans-serif;
  font-weight: 500;
  font-size: 16px;
  /* 阴影 */
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2),
  0 2px 4px -2px rgba(79, 70, 229, 0.2);
}

/* 悬停效果 */
.add-knowledge-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 10px -2px rgba(79, 70, 229, 0.3),
  0 4px 6px -4px rgba(79, 70, 229, 0.3);
}

/* 点击动画 */
.add-knowledge-button:active {
  transform: scale(0.98);
}

/* 光效装饰 */
.add-knowledge-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.3),
      transparent
  );
  transition: left 0.6s ease;
}

.add-knowledge-button:hover::after {
  left: 100%;
}
.add-question-button {
  /* 布局 */
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  flex-shrink: 0; /* 禁止高度压缩 */
  /* 视觉样式 */
  background: linear-gradient(135deg, #4f46e5 0%, #8b5cf6 100%);
  border-radius: 8px;
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;

  /* 文字样式 */
  color: white;
  font-family: 'Segoe UI', sans-serif;
  font-weight: 500;
  font-size: 16px;
  /* 阴影 */
  box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2),
  0 2px 4px -2px rgba(79, 70, 229, 0.2);
}

/* 悬停效果 */
.add-question-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 10px -2px rgba(79, 70, 229, 0.3),
  0 4px 6px -4px rgba(79, 70, 229, 0.3);
}

/* 点击动画 */
.add-question-button:active {
  transform: scale(0.98);
}

/* 光效装饰 */
.add-question-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.3),
      transparent
  );
  transition: left 0.6s ease;
}

.add-question-button:hover::after {
  left: 100%;
}
.plus-symbol-knowledge {
  font-size: 20px;
  font-weight: 300;
  flex-shrink: 0;  /* 禁止缩小 */
  transition: transform 0.3s ease;
}
.plus-symbol-question {
  font-size: 20px;
  font-weight: 300;
  flex-shrink: 0;  /* 禁止缩小 */
  transition: transform 0.3s ease;
}
/* 悬停时加号动画 */
.add-knowledge-button:hover .plus-symbol {
  transform: rotate(90deg) scale(1.2);
}
</style>