<template>
  <div class="register-container">
    <a-card class="register-card" title="注册">
      <a-form
        :model="formState"
        name="register"
        :label-col="{ span: 8 }"
        :wrapper-col="{ span: 16 }"
        autocomplete="off"
        @finish="onFinish"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[{ required: true, message: '请输入用户名！' }]"
        >
          <a-input v-model:value="formState.username" />
        </a-form-item>

        <a-form-item
          label="邮箱"
          name="email"
          :rules="[
            { required: true, message: '请输入邮箱！' },
            { type: 'email', message: '请输入有效的邮箱地址！' }
          ]"
        >
          <a-input v-model:value="formState.email" />
        </a-form-item>

        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码！' }]"
        >
          <a-input-password v-model:value="formState.password" />
        </a-form-item>

        <a-form-item
          label="确认密码"
          name="confirmPassword"
          :rules="[
            { required: true, message: '请确认密码！' },
            { validator: validateConfirmPassword }
          ]"
        >
          <a-input-password v-model:value="formState.confirmPassword" />
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
          <a-button type="primary" html-type="submit">注册</a-button>
          <a-button style="margin-left: 10px" @click="goToLogin">返回登录</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'

const router = useRouter()

const formState = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = async (rule, value) => {
  if (value !== formState.password) {
    throw new Error('两次输入的密码不一致！')
  }
}

const onFinish = async (values) => {
  try {
    await axios.post('http://localhost:8000/api/users/register', {
      username: values.username,
      email: values.email,
      password: values.password
    })
    
    message.success('注册成功')
    router.push('/login')
  } catch (error) {
    message.error('注册失败：' + (error.response?.data?.detail || error.message))
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.register-card {
  width: 400px;
}
</style> 