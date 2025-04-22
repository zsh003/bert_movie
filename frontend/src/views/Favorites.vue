<template>
  <div class="favorites-page">
    <h2>我的收藏</h2>
    <a-row :gutter="[16, 16]">
      <a-col :span="6" v-for="movie in favorites" :key="movie._id">
        <a-card hoverable>
          <template #cover>
            <img 
                :src="movie.img.content ? 'data:image/webp;base64,' + movie.img.content : ''" 
                :alt="movie.title"
                style="width: 100%; height: 300px; object-fit: contain;" 
              />
          </template>
          <template #actions>
            <a-button type="link" @click="goToMovie(movie.movie_id)">
              查看详情
            </a-button>
            <a-button type="link" danger @click="removeFavorite(movie.favorite_id)">
              取消收藏
            </a-button>
          </template>
          <a-card-meta :title="movie.title">
            <template #description>
              收藏于: {{ formatDate(movie.favorited_at) }}
            </template>
          </a-card-meta>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useUserStore } from '../stores/user'

interface Movie {
  _id: string;
  movie_id: string;
  title: string;
  poster: string;
  img: string;
  favorite_id: string;
  favorited_at: string;
}

export default defineComponent({
  name: 'FavoritesPage',
  setup() {
    const router = useRouter();
    const favorites = ref<Movie[]>([]);
    const loading = ref(false);

    const fetchFavorites = async () => {
      loading.value = true;
      try {
        const response = await axios.get('http://localhost:8000/api/favorites',
          { headers: { 'Authorization': `Bearer ${useUserStore().token}` } }
        );
        favorites.value = response.data;
        console.log(favorites.value);
      } catch (error) {
        message.error('获取收藏失败');
      }
      loading.value = false;
    };

    const removeFavorite = async (favoriteId: string) => {
      try {
        await axios.delete(`http://localhost:8000/api/favorites/${favoriteId}`
          , { headers: { 'Authorization': `Bearer ${useUserStore().token}` } }
        );
        message.success('已取消收藏');
        await fetchFavorites();
      } catch (error) {
        message.error('取消收藏失败');
      }
    };

    const goToMovie = (movieId: string) => {
      router.push(`/movie/${movieId}`);
    };

    const formatDate = (date: string) => {
      return new Date(date).toLocaleString('zh-CN');
    };

    onMounted(() => {
      fetchFavorites();
    });

    return {
      favorites,
      loading,
      removeFavorite,
      goToMovie,
      formatDate
    };
  }
});
</script>

<style scoped>
.favorites-page {
  padding: 24px;
}

.ant-card {
  width: 100%;
}

.ant-card-cover img {
  height: 300px;
  object-fit: cover;
}
</style> 