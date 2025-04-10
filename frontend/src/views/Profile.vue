<template>
  <div class="profile-container">
    <a-row :gutter="[24, 24]">
      <a-col :span="24">
        <a-card>
          <a-tabs v-model:activeKey="activeTab">
            <a-tab-pane key="info" tab="个人信息">
              <div class="profile-info">
                <div class="avatar-section">
                  <a-upload
                    v-model:file-list="fileList"
                    name="avatar"
                    list-type="picture-card"
                    class="avatar-uploader"
                    :show-upload-list="false"
                    :before-upload="beforeUpload"
                    @change="handleChange"
                  >
                    <img v-if="imageUrl" :src="imageUrl" alt="avatar" />
                    <div v-else>
                      <loading-outlined v-if="loading" />
                      <plus-outlined v-else />
                      <div class="ant-upload-text">上传头像</div>
                    </div>
                  </a-upload>
                </div>

                <a-form
                  :model="formState"
                  name="profile-form"
                  @finish="onFinish"
                  :label-col="{ span: 4 }"
                  :wrapper-col="{ span: 16 }"
                >
                  <a-form-item label="用户名" name="username">
                    <a-input v-model:value="formState.username" disabled />
                  </a-form-item>

                  <a-form-item label="邮箱" name="email">
                    <a-input v-model:value="formState.email" />
                  </a-form-item>

                  <a-form-item label="注册时间">
                    <span>{{ formatDate(formState.created_at) }}</span>
                  </a-form-item>

                  <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
                    <a-button type="primary" html-type="submit">保存修改</a-button>
                  </a-form-item>
                </a-form>
              </div>
            </a-tab-pane>

            <a-tab-pane key="settings" tab="账号设置">
              <a-form
                :model="passwordForm"
                name="password-form"
                @finish="onPasswordChange"
                :label-col="{ span: 4 }"
                :wrapper-col="{ span: 16 }"
              >
                <a-form-item
                  label="当前密码"
                  name="currentPassword"
                  :rules="[{ required: true, message: '请输入当前密码' }]"
                >
                  <a-input-password v-model:value="passwordForm.currentPassword" />
                </a-form-item>

                <a-form-item
                  label="新密码"
                  name="newPassword"
                  :rules="[{ required: true, message: '请输入新密码' }]"
                >
                  <a-input-password v-model:value="passwordForm.newPassword" />
                </a-form-item>

                <a-form-item
                  label="确认新密码"
                  name="confirmPassword"
                  :rules="[
                    { required: true, message: '请确认新密码' },
                    { validator: validateConfirmPassword }
                  ]"
                >
                  <a-input-password v-model:value="passwordForm.confirmPassword" />
                </a-form-item>

                <a-form-item :wrapper-col="{ offset: 4, span: 16 }">
                  <a-button type="primary" html-type="submit">修改密码</a-button>
                </a-form-item>
              </a-form>
            </a-tab-pane>

            <a-tab-pane key="activity" tab="我的动态">
              <a-list
                class="activity-list"
                :data-source="activities"
                :loading="loadingActivities"
              >
                <template #renderItem="{ item }">
                  <a-list-item>
                    <a-list-item-meta>
                      <template #title>
                        {{ item.type === 'review' ? '发表评论' : '收藏电影' }}
                      </template>
                      <template #description>
                        <div>
                          <router-link :to="`/movie/${item.movie_id}`">
                            {{ item.movie_title }}
                          </router-link>
                          <span class="activity-time">
                            {{ formatDate(item.created_at) }}
                          </span>
                        </div>
                        <div v-if="item.type === 'review'" class="activity-content">
                          {{ item.content }}
                        </div>
                      </template>
                    </a-list-item-meta>
                  </a-list-item>
                </template>
              </a-list>
            </a-tab-pane>
          </a-tabs>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '../stores/user'
import { LoadingOutlined, PlusOutlined } from '@ant-design/icons-vue'
import type { UploadChangeParam, UploadProps } from 'ant-design-vue'
import axios from 'axios'

const route = useRoute()
const userStore = useUserStore()
const activeTab = ref(route.query.tab?.toString() || 'info')

// 个人信息表单
const formState = reactive({
  username: userStore.user?.username || '',
  email: userStore.user?.email || '',
  created_at: userStore.user?.created_at || ''
})

// 密码修改表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 头像上传
const loading = ref<boolean>(false)
const imageUrl = ref<string>(userStore.user?.avatar || '')
const fileList = ref([])

// 用户动态
const activities = ref([])
const loadingActivities = ref(false)

const beforeUpload = (file: File) => {
  const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
  if (!isJpgOrPng) {
    message.error('只能上传 JPG/PNG 格式的图片！')
  }
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isLt2M) {
    message.error('图片大小不能超过 2MB！')
  }
  return isJpgOrPng && isLt2M
}

const handleChange = (info: UploadChangeParam) => {
  if (info.file.status === 'uploading') {
    loading.value = true
    return
  }
  if (info.file.status === 'done') {
    loading.value = false
    imageUrl.value = info.file.response.url
  }
}

const validateConfirmPassword = async (_rule: any, value: string) => {
  if (value !== passwordForm.newPassword) {
    throw new Error('两次输入的密码不一致！')
  }
}

const onFinish = async (values: any) => {
  try {
    await axios.put(
      'http://localhost:8000/api/users/profile',
      values,
      {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      }
    )
    message.success('个人信息更新成功')
    userStore.setUser({
      ...userStore.user!,
      email: values.email
    })
  } catch (error: any) {
    message.error('更新失败：' + error.response?.data?.detail || error.message)
  }
}

const onPasswordChange = async (values: any) => {
  try {
    await axios.put(
      'http://localhost:8000/api/users/password',
      values,
      {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      }
    )
    message.success('密码修改成功')
    passwordForm.currentPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
  } catch (error: any) {
    message.error('密码修改失败：' + error.response?.data?.detail || error.message)
  }
}

const fetchActivities = async () => {
  loadingActivities.value = true
  try {
    const response = await axios.get(
      'http://localhost:8000/api/users/activities',
      {
        headers: {
          Authorization: `Bearer ${userStore.token}`
        }
      }
    )
    activities.value = response.data
  } catch (error: any) {
    message.error('获取动态失败：' + error.response?.data?.detail || error.message)
  } finally {
    loadingActivities.value = false
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchActivities()
})
</script>

<style scoped>
.profile-container {
  padding: 24px;
}

.profile-info {
  max-width: 800px;
  margin: 0 auto;
}

.avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.avatar-uploader {
  display: inline-block;
}

:deep(.ant-upload.ant-upload-select-picture-card) {
  width: 128px;
  height: 128px;
  border-radius: 50%;
}

:deep(.ant-upload-select-picture-card img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.activity-list {
  margin-top: 16px;
}

.activity-time {
  margin-left: 16px;
  color: #999;
  font-size: 12px;
}

.activity-content {
  margin-top: 8px;
  color: #666;
}
</style> 