<template>
  <div class="activities-page">
    <h2>我的动态</h2>
    <a-timeline>
      <a-timeline-item v-for="activity in activities" :key="activity.created_at">
        <template #dot>
          <a-icon :type="getActivityIcon(activity.type)" :style="{ fontSize: '16px' }" />
        </template>
        <div class="activity-content">
          <div class="activity-header">
            <router-link :to="`/movie/${activity.movie_id}`">{{ activity.movie_title }}</router-link>
            <span class="activity-time">{{ formatDate(activity.created_at) }}</span>
          </div>
          <div v-if="activity.type === 'review'" class="review-content">
            <p>{{ activity.content }}</p>
            <a-tag :color="getSentimentColor(activity.sentiment)">
              {{ getSentimentText(activity.sentiment) }}
            </a-tag>
          </div>
          <div v-else class="favorite-content">
            收藏了这部电影
          </div>
        </div>
      </a-timeline-item>
    </a-timeline>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import axios from 'axios';

interface Activity {
  type: 'review' | 'favorite';
  movie_id: string;
  movie_title: string;
  content?: string;
  sentiment?: string;
  created_at: string;
}

export default defineComponent({
  name: 'ActivitiesPage',
  setup() {
    const activities = ref<Activity[]>([]);
    const loading = ref(false);

    const fetchActivities = async () => {
      loading.value = true;
      try {
        const response = await axios.get('http://localhost:8000/api/users/activities');
        activities.value = response.data;
      } catch (error) {
        message.error('获取动态失败');
      }
      loading.value = false;
    };

    const getActivityIcon = (type: string) => {
      return type === 'review' ? 'comment' : 'star';
    };

    const formatDate = (date: string) => {
      return new Date(date).toLocaleString('zh-CN');
    };

    const getSentimentColor = (sentiment?: string) => {
      const colors = {
        positive: 'success',
        negative: 'error',
        neutral: 'warning'
      };
      return colors[sentiment || ''] || 'default';
    };

    const getSentimentText = (sentiment?: string) => {
      const texts = {
        positive: '积极',
        negative: '消极',
        neutral: '中性'
      };
      return texts[sentiment || ''] || sentiment;
    };

    onMounted(() => {
      fetchActivities();
    });

    return {
      activities,
      loading,
      getActivityIcon,
      formatDate,
      getSentimentColor,
      getSentimentText
    };
  }
});
</script>

<style scoped>
.activities-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.activity-content {
  margin-bottom: 16px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.activity-time {
  color: #999;
  font-size: 12px;
}

.review-content {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin-top: 8px;
}

.favorite-content {
  color: #666;
}
</style> 