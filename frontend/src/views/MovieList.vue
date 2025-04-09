<template>
  <div class="movie-list">
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <h1>电影列表</h1>
      </a-col>
      <a-col :xs="24" :sm="12" :md="8" :lg="6" v-for="movie in movies" :key="movie.movie_id">
        <a-card hoverable @click="goToDetail(movie.movie_id)">
          <template #title>{{ movie.title }}</template>
          <div class="movie-genre">{{ movie.genre }}</div>
          <div class="movie-desc">{{ movie.description.substring(0, 30) }}...</div>
          <img
            :src="'data:image/webp;base64,' + movie.img.content"
            :alt="movie.title"
            class="movie-poster"
          />
        </a-card>
      </a-col>
    </a-row>
    <div class="pagination">
      <a-pagination
        v-model:current="currentPage"
        :total="total"
        :pageSize="pageSize"
        @change="handlePageChange"
        show-size-changer
        :pageSizeOptions="['12', '24', '36', '48']"
        @showSizeChange="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const movies = ref([])
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(100) // 设置一个初始值，后续可以从后端获取实际总数

const fetchMovies = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/movies?skip=${(currentPage.value - 1) * pageSize.value}&limit=${pageSize.value}`)
    movies.value = response.data
  } catch (error) {
    console.error('Error fetching movies:', error)
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchMovies()
}

const handlePageSizeChange = (current, size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchMovies()
}

const goToDetail = (movieId) => {
  router.push(`/movie/${movieId}`)
}

onMounted(() => {
  fetchMovies()
})
</script>

<style scoped>
.movie-list {
  padding: 24px;
}

.movie-desc {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
  padding: 5px;
}

.movie-poster {
  width: 100%;
  max-height: 600px;
  object-fit: cover;
  border-radius: 8px;
}

.movie-genre {
  color: #666;
  font-size: 12px;
  padding-bottom: 5px;
}

.pagination {
  margin-top: 24px;
  text-align: center;
}

:deep(.ant-card) {
  height: 100%;
}

:deep(.ant-card-cover) {
  height: 300px;
  overflow: hidden;
}

:deep(.ant-card-cover img) {
  height: 100%;
  object-fit: cover;
}

:deep(.ant-card-body) {
  padding: 16px;
}
</style>
