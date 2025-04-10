<template>
  <div class="admin-container">
    <a-row :gutter="[24, 24]">
      <a-col :span="24">
        <h1>管理员控制台</h1>
      </a-col>

      <!-- 用户管理 -->
      <a-col :span="24">
        <a-card title="用户管理">
          <a-table :columns="userColumns" :data-source="users" :loading="loading">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'action'">
                <a-button
                  type="link"
                  danger
                  @click="handleDeleteUser(record)"
                >
                  删除
                </a-button>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>

      <!-- 评论情感分析统计 -->
      <a-col :xs="24" :lg="12">
        <a-card title="评论情感分布趋势">
          <div ref="sentimentTrendChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 用户活跃度分析 -->
      <a-col :xs="24" :lg="12">
        <a-card title="用户活跃度分析">
          <div ref="userActivityChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 评论长度分布 -->
      <a-col :xs="24" :lg="12">
        <a-card title="评论长度分布">
          <div ref="commentLengthChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 电影评分分布 -->
      <a-col :xs="24" :lg="12">
        <a-card title="电影评分分布">
          <div ref="movieRatingChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()
const loading = ref(false)
const users = ref([])

const userColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '角色',
    dataIndex: 'is_admin',
    key: 'is_admin',
    customRender: ({ text }) => text ? '管理员' : '普通用户',
  },
  {
    title: '操作',
    key: 'action',
  },
]

// 图表引用
const sentimentTrendChartRef = ref(null)
const userActivityChartRef = ref(null)
const commentLengthChartRef = ref(null)
const movieRatingChartRef = ref(null)

// 初始化图表
let sentimentTrendChart = null
let userActivityChart = null
let commentLengthChart = null
let movieRatingChart = null

const initCharts = () => {
  sentimentTrendChart = echarts.init(sentimentTrendChartRef.value)
  userActivityChart = echarts.init(userActivityChartRef.value)
  commentLengthChart = echarts.init(commentLengthChartRef.value)
  movieRatingChart = echarts.init(movieRatingChartRef.value)
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/api/users/users', {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    users.value = response.data
  } catch (error) {
    message.error('获取用户列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 删除用户
const handleDeleteUser = async (user) => {
  try {
    await axios.delete(`http://localhost:8000/api/users/${user.id}`, {
      headers: {
        'Authorization': `Bearer ${userStore.token}`
      }
    })
    message.success('删除成功')
    await fetchUsers()
  } catch (error) {
    message.error('删除失败：' + error.message)
  }
}

// 更新情感分析趋势图表
const updateSentimentTrendChart = (data) => {
  sentimentTrendChart.setOption({
    title: {
      text: '评论情感分布趋势'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['正面', '中性', '负面']
    },
    xAxis: {
      type: 'category',
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '正面',
        type: 'line',
        data: data.positive
      },
      {
        name: '中性',
        type: 'line',
        data: data.neutral
      },
      {
        name: '负面',
        type: 'line',
        data: data.negative
      }
    ]
  })
}

// 更新用户活跃度图表
const updateUserActivityChart = (data) => {
  userActivityChart.setOption({
    title: {
      text: '用户活跃度分析'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: data.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: data.counts
      }
    ]
  })
}

// 更新评论长度分布图表
const updateCommentLengthChart = (data) => {
  commentLengthChart.setOption({
    title: {
      text: '评论长度分布'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: [
          { value: data.short, name: '短评论 (<50字)' },
          { value: data.medium, name: '中等评论 (50-200字)' },
          { value: data.long, name: '长评论 (>200字)' }
        ]
      }
    ]
  })
}

// 更新电影评分分布图表
const updateMovieRatingChart = (data) => {
  movieRatingChart.setOption({
    title: {
      text: '电影评分分布'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['1分', '2分', '3分', '4分', '5分']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: data.ratings
      }
    ]
  })
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    // 获取情感分析趋势数据
    const sentimentTrendResponse = await axios.get('http://localhost:8000/api/analysis/sentiment-trend')
    updateSentimentTrendChart(sentimentTrendResponse.data)

    // 获取用户活跃度数据
    const userActivityResponse = await axios.get('http://localhost:8000/api/analysis/user-activity-trend')
    updateUserActivityChart(userActivityResponse.data)

    // 获取评论长度分布数据
    const commentLengthResponse = await axios.get('http://localhost:8000/api/analysis/comment-length-distribution')
    updateCommentLengthChart(commentLengthResponse.data)

    // 获取电影评分分布数据
    const movieRatingResponse = await axios.get('http://localhost:8000/api/analysis/movie-rating-distribution')
    updateMovieRatingChart(movieRatingResponse.data)
  } catch (error) {
    message.error('获取统计数据失败：' + error.message)
  }
}

onMounted(async () => {
  initCharts()
  await fetchUsers()
  await fetchStatistics()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    sentimentTrendChart?.resize()
    userActivityChart?.resize()
    commentLengthChart?.resize()
    movieRatingChart?.resize()
  })
})
</script>

<style scoped>
.admin-container {
  padding: 24px;
}
</style> 