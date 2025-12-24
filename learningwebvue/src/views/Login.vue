<template>
  <div class="login-container">
    <!-- 外层容器确保整体居中 -->
    <div class="login-wrapper">
      <div class="login-card bg-white rounded-2xl shadow-lg p-8 max-w-md w-full transition-all duration-300 hover:shadow-xl">
        <div class="text-center mb-8">
          <h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-gray-800 mb-2">账户登录</h2>
          <p class="text-gray-500">请输入您的账号信息</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- 用户名输入 -->
          <div class="space-y-2">
            <label for="username" class="block text-sm font-medium text-gray-700">用户名</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                <i class="fa fa-user"></i>
              </span>
              <input
                type="text"
                id="username"
                v-model="form.username"
                class="input-field pl-10"
                placeholder="请输入用户名"
                required
              >
            </div>
            <p v-if="errors.username" class="text-danger text-sm">{{ errors.username }}</p>
          </div>

          <!-- 密码输入 -->
          <div class="space-y-2">
            <label for="password" class="block text-sm font-medium text-gray-700">密码</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                <i class="fa fa-lock"></i>
              </span>
              <input
                :type="showPassword ? 'text' : 'password'"
                id="password"
                v-model="form.password"
                class="input-field pl-10"
                placeholder="请输入密码"
                required
              >
            </div>
            <p v-if="errors.password" class="text-danger text-sm">{{ errors.password }}</p>
          </div>

          <!-- 验证码（已增大尺寸） -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">验证码</label>
            <div class="flex gap-3">
              <div class="flex-1">
                <input
                  type="text"
                  id="captchaInput"
                  v-model="form.captcha"
                  class="input-field"
                  placeholder="请输入验证码"
                  required
                >
                <p v-if="errors.captcha" class="text-danger text-sm">{{ errors.captcha }}</p>
              </div>
              <!-- 增大验证码容器尺寸 -->
              <div class="w-48 captcha-box cursor-pointer select-none overflow-hidden" @click="refreshCaptcha">
                <canvas ref="captchaCanvas" width="192" height="72"></canvas>
                <div class="absolute right-2 top-2 text-xs text-gray-500 hover:text-primary">
                  <i class="fa fa-refresh"></i>
                </div>
              </div>
            </div>
          </div>

          <!-- 登录按钮 -->
          <button type="submit" class="btn-primary">
            <i class="fa fa-sign-in mr-2"></i>登录
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import router from "@/router/index.js";

// 表单数据
const form = reactive({
  username: '',
  password: '',
  captcha: ''
});

// 错误信息
const errors = reactive({
  username: '',
  password: '',
  captcha: ''
});

// 密码显示控制
const showPassword = ref(false);

// 验证码相关
const captchaCanvas = ref(null);
let captchaCode = '';

// 生成随机验证码（适配增大后的尺寸）
const generateCaptcha = () => {
  if (!captchaCanvas.value) return;

  const ctx = captchaCanvas.value.getContext('2d');
  const width = captchaCanvas.value.width; // 192px
  const height = captchaCanvas.value.height; // 72px

  // 清空画布
  ctx.clearRect(0, 0, width, height);

  // 生成随机字符串(4位)
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  captchaCode = '';
  for (let i = 0; i < 3; i++) {
    captchaCode += chars.charAt(Math.floor(Math.random() * chars.length));
  }

  // 绘制背景
  ctx.fillStyle = '#F5F7FA';
  ctx.fillRect(0, 0, width, height);

  // 绘制干扰线（适配大尺寸）
  for (let i = 0; i < 8; i++) {
    ctx.strokeStyle = `rgba(${Math.random() * 100}, ${Math.random() * 150}, ${Math.random() * 255}, 0.5)`;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(Math.random() * width, Math.random() * height);
    ctx.lineTo(Math.random() * width, Math.random() * height);
    ctx.stroke();
  }

  // 绘制验证码（增大字体适配尺寸）
  ctx.font = 'bold 34px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  for (let i = 0; i < captchaCode.length; i++) {
    const char = captchaCode.charAt(i);
    ctx.fillStyle = `rgb(${Math.random() * 50}, ${Math.random() * 100}, ${Math.random() * 200})`;
    ctx.save();
    ctx.translate(48 * i + 48, height / 2); // 适配192宽度的位置计算
    ctx.rotate((Math.random() - 0.5) * 0.4);
    ctx.fillText(char, 0, 0);
    ctx.restore();
  }

  // 绘制干扰点（增加数量适配大尺寸）
  for (let i = 0; i < 80; i++) {
    ctx.fillStyle = `rgba(${Math.random() * 255}, ${Math.random() * 255}, ${Math.random() * 255}, 0.5)`;
    ctx.beginPath();
    ctx.arc(Math.random() * width, Math.random() * height, 1.2, 0, 2 * Math.PI);
    ctx.fill();
  }
};

// 刷新验证码
const refreshCaptcha = () => {
  generateCaptcha();
  form.captcha = '';
  errors.captcha = '';
};

// 表单验证
const validateForm = () => {
  let isValid = true;

  // 重置错误
  errors.username = '';
  errors.password = '';
  errors.captcha = '';

  // 验证用户名
  if (!form.username.trim()) {
    errors.username = '用户名不能为空';
    isValid = false;
  }

  // 验证密码
  if (form.password.length < 6) {
    errors.password = '密码长度不能少于6位';
    isValid = false;
  }

  // 验证验证码
  if (form.captcha.toUpperCase() !== captchaCode.toUpperCase()) {
    errors.captcha = '验证码不正确';
    isValid = false;
  }

  return isValid;
};

// 处理登录
// 处理登录
const handleLogin = async () => {
  if (validateForm()) {
    // try {
      // // 发送登录请求到后端
      // const response = await fetch('http://localhost:8000/loginRegister', {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify(loginData),
      //   // 允许跨域请求携带凭证（如 cookies）
      //   credentials: 'include'
      // })
      router.push('/NoteList');
    //
    //   const result = await response.json();
    //   response.ok = true
    //   // 处理后端响应
    //   if (response.ok) {
    //     // 登录成功 - 后端返回成功状态
    //     if (result.success) {
    //       // 可以存储 token 到本地存储（如果后端返回）
    //       if (result.token) {
    //         localStorage.setItem('token', result.token);
    //       }
    //       // 跳转到笔记列表页
    //       router.push('/NoteList');
    //     } else {
    //       // 后端返回业务错误（如用户名密码错误）
    //       alert(result.message || '登录失败，请检查账号信息');
    //       // 刷新验证码
    //       refreshCaptcha();
    //     }
    //   } else {
    //     // HTTP 错误状态（4xx/5xx）
    //     throw new Error(result.message || `请求失败: ${response.status}`);
    //   }
    // } catch (error) {
    //   // 捕获网络错误或其他异常
    //   console.error('登录请求失败:', error);
    //   alert('登录失败，请检查网络连接或稍后重试');
    //   // 刷新验证码
    //   refreshCaptcha();
    // }
  //
  }
};

// 组件挂载后初始化验证码
onMounted(() => {
  nextTick(() => {
    generateCaptcha();
  });
});
</script>

<style scoped>
/* 外层容器确保全屏居中 */
.login-container {
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

/* 中间包裹层确保内容居中显示 */
.login-wrapper {
  width: 100%;
  max-width: 500px; /* 限制最大宽度 */
}

.login-card {
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  width: 100%;
  transition: all 0.3s ease;
}

.login-card:hover {
  box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.1);
}

.input-field {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
  outline: none;
  transition: all 0.2s ease;
  font-size: 1rem;
}

.input-field:focus {
  border-color: #165DFF;
  box-shadow: 0 0 0 4px rgba(22, 93, 255, 0.1);
}

.btn-primary {
  width: 100%;
  background-color: #165DFF;
  color: white;
  font-weight: 500;
  padding: 0.75rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  border: none;
  font-size: 1rem;
  cursor: pointer;
}

.btn-primary:hover {
  background-color: rgba(22, 93, 255, 0.9);
}

.btn-primary:active {
  transform: scale(0.98);
}

/* 增大验证码容器尺寸 */
.captcha-box {
  position: relative;
  background-color: #F5F7FA;
  border-radius: 0.5rem;
  height: 4.5rem; /* 增大高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  overflow: hidden;
  border: 1px solid #d1d5db;
}

.text-danger {
  color: #F53F3F;
}
</style>