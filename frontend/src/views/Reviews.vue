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
          <a-card hoverable>
            <div style="display: flex; gap: 20px;">
              <!-- 左侧内容 -->
              <div style="flex: 1;">
                <a-card-meta>
                  <template #title>
                    <router-link 
                      :to="'/movie/' + item.movie_id"
                      style="font-size: 18px; font-weight: 500;"
                    >
                      {{ item.movie_title }}
                    </router-link>
                    <span style="margin-left: 12px; color: #888; font-size: 12px;">
                      {{ formatDate(item.created_at) }}
                    </span>
                  </template>
                </a-card-meta>

                <div class="review-content">
                  <p style="margin: 12px 0; font-size: 14px; line-height: 1.6;">{{ item.content }}</p>
                  <a-tag 
                    :color="getSentimentColor(item.sentiment)"
                    style="margin-bottom: 12px;"
                  >
                    {{ getSentimentText(item.sentiment) }}
                  </a-tag>
                </div>
              </div>

              <!-- 右侧海报 -->
              <div v-if="item.movie_img" style="width: 200px;">
                <img 
                  :src="'data:image/webp;base64,' + item.movie_img"
                  style="width: 100%; height: 150px; object-fit: cover; border-radius: 4px;"
                />
              </div>
            </div>

            <!-- 操作按钮移动到卡片底部 -->
            <template #actions>
              <a-button type="link" danger @click="deleteReview(item._id)">
                删除评论
              </a-button>
            </template>
          </a-card>
        </a-list-item>
      </template>
    </a-list>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';
import { useUserStore } from '../stores/user'

export default defineComponent({
  name: 'ReviewsPage',
  setup() {
    const reviews = ref([]);
    const loading = ref(false);

    const fetchReviews = async () => {
      loading.value = true;
      try {
        const response = await axios.get('http://localhost:8000/api/reviews/user/me',
          { headers: { 'Authorization': `Bearer ${useUserStore().token}` } }
        );
        reviews.value = response.data;
      } catch (error) {
        message.error('获取评论失败');
      }
      loading.value = false;
    };

    const deleteReview = async (reviewId: string) => {
      try {
        await axios.delete(`http://localhost:8000/api/reviews/${reviewId}`,
          { headers: { 'Authorization': `Bearer ${useUserStore().token}` } }
        );
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