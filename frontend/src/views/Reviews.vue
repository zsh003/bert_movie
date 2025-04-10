<template>
  <div class="reviews-page">
    <h2>我的评论</h2>
    <a-list
      :data-source="reviews"
      :loading="loading"
      item-layout="vertical"
    >
      <template #renderItem="{ item }">
        <a-list-item>
          <template #extra>
            <img
              width="272"
              alt="电影海报"
              :src="item.movie_poster"
            />
          </template>
          <a-list-item-meta
            :description="formatDate(item.created_at)"
          >
            <template #title>
              <router-link :to="'/movie/' + item.movie_id">{{ item.movie_title }}</router-link>
            </template>
          </a-list-item-meta>
          <div class="review-content">
            <p>{{ item.content }}</p>
            <a-tag :color="getSentimentColor(item.sentiment)">
              {{ getSentimentText(item.sentiment) }}
            </a-tag>
          </div>
          <template #actions>
            <a-button type="link" danger @click="deleteReview(item._id)">
              删除评论
            </a-button>
          </template>
        </a-list-item>
      </template>
    </a-list>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';

export default defineComponent({
  name: 'ReviewsPage',
  setup() {
    const reviews = ref([]);
    const loading = ref(false);

    const fetchReviews = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/reviews/user/me');
        reviews.value = response.data;
      } catch (error) {
        message.error('获取评论失败');
      }
      loading.value = false;
    };

    const deleteReview = async (reviewId: string) => {
      try {
        await axios.delete(`/api/reviews/${reviewId}`);
        message.success('评论已删除');
        await fetchReviews();
      } catch (error) {
        message.error('删除评论失败');
      }
    };

    const formatDate = (date: string) => {
      return new Date(date).toLocaleString('zh-CN');
    };

    const getSentimentColor = (sentiment: string) => {
      const colors = {
        positive: 'success',
        negative: 'error',
        neutral: 'warning'
      };
      return colors[sentiment] || 'default';
    };

    const getSentimentText = (sentiment: string) => {
      const texts = {
        positive: '积极',
        negative: '消极',
        neutral: '中性'
      };
      return texts[sentiment] || sentiment;
    };

    onMounted(() => {
      fetchReviews();
    });

    return {
      reviews,
      loading,
      deleteReview,
      formatDate,
      getSentimentColor,
      getSentimentText
    };
  }
});
</script>

<style scoped>
.reviews-page {
  padding: 24px;
}

.review-content {
  margin: 16px 0;
}
</style> 