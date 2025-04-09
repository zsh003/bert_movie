<template>
  <div class="analysis">
    <a-row :gutter="[24, 24]">
      <a-col :span="24">
        <h1>数据分析</h1>
      </a-col>
      
      <!-- 电影类型分布 -->
      <a-col :xs="24" :lg="12">
        <a-card title="电影类型分布">
          <div ref="genreChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 用户活跃度 -->
      <a-col :xs="24" :lg="12">
        <a-card title="用户活跃度排行">
          <div ref="userActivityChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 评论情感分析 -->
      <a-col :xs="24" :lg="12">
        <a-card title="评论情感分析">
          <a-select
            v-model:value="selectedMovie"
            style="width: 100%; margin-bottom: 16px"
            placeholder="请选择电影"
            @change="fetchSentimentData"
          >
            <a-select-option v-for="movie in movies" :key="movie.movie_id" :value="movie.movie_id">
              {{ movie.title }}
            </a-select-option>
          </a-select>
          <div ref="sentimentChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>

      <!-- 词云图 -->
      <a-col :xs="24" :lg="12">
        <a-card title="评论词云">
          <div ref="wordCloudChartRef" style="height: 400px"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import 'echarts-wordcloud'

const genreChartRef = ref(null)
const userActivityChartRef = ref(null)
const sentimentChartRef = ref(null)
const wordCloudChartRef = ref(null)

const movies = ref([])
const selectedMovie = ref('')

let genreChart = null
let userActivityChart = null
let sentimentChart = null
let wordCloudChart = null

// 初始化图表
const initCharts = () => {
  genreChart = echarts.init(genreChartRef.value)
  userActivityChart = echarts.init(userActivityChartRef.value)
  sentimentChart = echarts.init(sentimentChartRef.value)
  wordCloudChart = echarts.init(wordCloudChartRef.value)
}

// 获取电影类型分布数据
const fetchGenreData = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/movies/genres/stats')
    const data = response.data
    
    genreChart.setOption({
      title: {
        text: '电影类型分布'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          type: 'pie',
          radius: '70%',
          data: data.map(item => ({
            name: item._id,
            value: item.count
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  } catch (error) {
    console.error('Error fetching genre data:', error)
  }
}

// 获取用户活跃度数据
const fetchUserActivity = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/analysis/user-activity')
    const data = response.data
    
    userActivityChart.setOption({
      title: {
        text: '用户活跃度排行'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: data.map(item => item._id)
      },
      series: [
        {
          type: 'bar',
          data: data.map(item => item.review_count)
        }
      ]
    })
  } catch (error) {
    console.error('Error fetching user activity:', error)
  }
}

// 获取情感分析数据
const fetchSentimentData = async () => {
  if (!selectedMovie.value) return
  
  try {
    const response = await axios.get(`http://localhost:8000/api/analysis/sentiment/${selectedMovie.value}`)
    const data = response.data
    
    sentimentChart.setOption({
      title: {
        text: '评论情感分布'
      },
      tooltip: {
        trigger: 'item'
      },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '20',
              fontWeight: 'bold'
            }
          },
          labelLine: {
            show: false
          },
          data: [
            { value: data.positive, name: '正面' },
            { value: data.neutral, name: '中性' },
            { value: data.negative, name: '负面' }
          ]
        }
      ]
    })
  } catch (error) {
    console.error('Error fetching sentiment data:', error)
  }
}

// 获取词云数据
const fetchWordCloud = async () => {
  if (!selectedMovie.value) return
  
  try {
    const response = await axios.get(`http://localhost:8000/api/analysis/word-cloud/${selectedMovie.value}`)
    const data = response.data
    
    wordCloudChart.setOption({
      series: [{
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '70%',
        height: '80%',
        right: null,
        bottom: null,
        sizeRange: [12, 60],
        rotationRange: [-90, 90],
        rotationStep: 45,
        gridSize: 8,
        drawOutOfBound: false,
        textStyle: {
          fontFamily: 'sans-serif',
          fontWeight: 'bold',
          color: function () {
            return 'rgb(' + [
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160),
              Math.round(Math.random() * 160)
            ].join(',') + ')'
          }
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            shadowBlur: 10,
            shadowColor: '#333'
          }
        },
        data: data.map(item => ({
          name: item.word,
          value: item.count
        }))
      }]
    })
  } catch (error) {
    console.error('Error fetching word cloud data:', error)
  }
}

// 获取电影列表
const fetchMovies = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/movies')
    movies.value = response.data
  } catch (error) {
    console.error('Error fetching movies:', error)
  }
}

onMounted(async () => {
  initCharts()
  await fetchMovies()
  await fetchGenreData()
  await fetchUserActivity()
  
  window.addEventListener('resize', () => {
    genreChart?.resize()
    userActivityChart?.resize()
    sentimentChart?.resize()
    wordCloudChart?.resize()
  })
})

// 监听选中电影变化
watch(selectedMovie, () => {
  fetchSentimentData()
  fetchWordCloud()
})
</script>

<style scoped>
.analysis {
  padding: 24px;
}
</style> 