<template>
  <div class="login-container">
    <a-card class="login-card" title="登录">
      <a-form
        :model="formState"
        name="basic"
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
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码！' }]"
        >
          <a-input-password v-model:value="formState.password" />
        </a-form-item>

        <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
          <a-button type="primary" html-type="submit">登录</a-button>
          <a-button style="margin-left: 10px" @click="goToRegister">注册</a-button>
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
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

const formState = reactive({
  username: '',
  password: ''
})

const onFinish = async (values) => {
  try {
    const params = new URLSearchParams()
    params.append('username', values.username)
    params.append('password', values.password)

    const response = await axios.post('http://localhost:8000/api/users/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'  // 必须指定这个请求头
      }
    })
    const { access_token } = response.data

    // 保存token
    userStore.setToken(access_token)
    
    // 获取用户信息
    const userResponse = await axios.get('http://localhost:8000/api/users/me', {
      headers: {
        'Authorization': `Bearer ${access_token}`
      }
    })
    
    userStore.setUser(userResponse.data)
    message.success('登录成功')
    
    // 根据用户角色跳转
    if (userResponse.data.is_admin) {
      router.push('/admin')
    } else {
      router.push('/')
    }
  } catch (error) {
    message.error('登录失败：' + (error.response?.data?.detail || error.message))
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}
</style> 