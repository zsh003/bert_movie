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
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const movie = ref(null)

const fetchMovieDetail = async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/movies/${route.params.id}`)
    movie.value = response.data
  } catch (error) {
    console.error('Error fetching movie details:', error)
  }
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
</style>
