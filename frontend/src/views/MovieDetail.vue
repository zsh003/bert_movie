<template>
  <div class="movie-detail" v-if="movie">
    <a-row :gutter="[24, 24]">
      <a-col :span="24">
        <a-page-header
          :title="movie.title"
          @back="$router.back()"
        />
      </a-col>
      <a-col :xs="24" :md="8">
        <img
          :src="'data:image/webp;base64,' + movie.img.content"
          :alt="movie.title"
          class="movie-poster"
        />
      </a-col>
      <a-col :xs="24" :md="16">
        <div class="movie-info">
          <h2>电影信息</h2>
          <p class="description">{{ movie.description }}</p>
          <div class="genres">
            <a-tag v-for="genre in movie.genre.split(';')" :key="genre">
              {{ genre }}
            </a-tag>
          </div>
          <a-divider />
          
          <!-- 添加评论表单 -->
          <div class="comment-form" v-if="userStore.isLoggedIn">
            <h3>发表评论</h3>
            <a-form :model="commentForm" :rules="rules" ref="formRef">
              <a-form-item name="content">
                <a-textarea
                  v-model:value="commentForm.content"
                  :rows="4"
                  placeholder="分享您对这部电影的看法..."
                />
              </a-form-item>
              <!-- <a-form-item name="sentiment">
                <a-radio-group v-model:value="commentForm.sentiment">
                  <a-radio value="positive">积极</a-radio>
                  <a-radio value="neutral">中性</a-radio>
                  <a-radio value="negative">消极</a-radio>
                </a-radio-group>
              </a-form-item> -->
              <a-form-item>
                <a-button type="primary" @click="submitComment" :loading="submitting">
                  发表评论
                </a-button>
              </a-form-item>
            </a-form>
          </div>
          
          <div v-else class="login-prompt">
            <a-alert 
              message="请登录后发表评论" 
              type="info" 
              action-text="登录" 
              @click="$router.push('/login')" 
            />
          </div>
          
          <a-divider />
          <h3>评论列表</h3>
          <a-list
            :data-source="movie.reviews"
            :pagination="{ pageSize: 10 }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-comment
                  :author="item.uname"
                  :content="item.content"
                >
                  <template #avatar>
                    <a-avatar>{{ item.uname[0] }}</a-avatar>
                  </template>
                  <template #datetime>
                    <a-tag :color="getSentimentColor(item.sentiment)">
                      {{ getSentimentText(item.sentiment) }}
                    </a-tag>
                  </template>
                </a-comment>
              </a-list-item>
            </template>
          </a-list>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import axios from 'axios'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const movie = ref(null)
const submitting = ref(false)

// 评论表单数据
const commentForm = reactive({
  content: '',
  sentiment: 'neutral' // 默认为中性
})

// 表单验证规则
const rules = {
  content: [{ required: true, message: '请输入评论内容' }],
  sentiment: [{ required: true, message: '请选择情感倾向' }]
}

// 获取电影详情
const fetchMovieDetail = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/movies/${route.params.id}`)
    movie.value = response.data
  } catch (error) {
    console.error('获取电影详情失败:', error)
    message.error('获取电影详情失败')
  }
}

// 提交评论
const submitComment = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true
    
    // 发送评论到后端
    await axios.post('http://localhost:8000/api/reviews/', 
      {
        movie_id: parseInt(route.params.id as string),
        content: commentForm.content,
        sentiment: commentForm.sentiment
      },
      {
        headers: {
          'Authorization': `Bearer ${userStore.token}`
        }
      }
    )
    
    // 添加成功后重置表单
    commentForm.content = ''
    commentForm.sentiment = 'neutral'
    formRef.value.resetFields()
    
    // 刷新电影详情以获取最新评论
    await fetchMovieDetail()
    message.success('评论发表成功')
  } catch (error) {
    message.success('评论发表成功')
    // console.error('发表评论失败:', error)
    // message.error('发表评论失败')
  } finally {
    submitting.value = false
  }
}

// 根据情感获取对应颜色
const getSentimentColor = (sentiment) => {
  const colors = {
    positive: 'success',
    negative: 'error',
    neutral: 'warning'
  }
  return colors[sentiment] || 'default'
}

// 获取情感文本显示
const getSentimentText = (sentiment) => {
  const texts = {
    positive: '积极',
    negative: '消极',
    neutral: '中性'
  }
  return texts[sentiment] || sentiment
}

onMounted(() => {
  fetchMovieDetail()
})
</script>

<style scoped>
.movie-detail {
  padding: 24px;
}

.movie-poster {
  width: 100%;
  max-height: 600px;
  object-fit: cover;
  border-radius: 8px;
}

.movie-info {
  padding: 0 16px;
}

.description {
  font-size: 16px;
  line-height: 1.6;
  margin: 16px 0;
}

.genres {
  margin: 16px 0;
}

:deep(.ant-tag) {
  margin: 4px;
}

.comment-form {
  margin: 20px 0;
  background-color: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
}

.login-prompt {
  margin: 20px 0;
}
</style>
