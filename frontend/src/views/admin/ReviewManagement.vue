<template>
  <div class="review-management">
    <div class="page-header">
      <h2>影评数据管理</h2>
    </div>

    <a-table
      :columns="columns"
      :data-source="reviews"
      :loading="loading"
      :pagination="{ pageSize: 10 }"
      rowKey="_id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'sentiment'">
          <a-tag :color="getSentimentColor(record.sentiment)">
            {{ getSentimentText(record.sentiment) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="showEditModal(record)">编辑</a-button>
            <a-popconfirm
              title="确定要删除这条评论吗？"
              @confirm="handleDelete(record._id)"
            >
              <a-button type="link" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 编辑评论的模态框 -->
    <a-modal
      title="编辑评论"
      :visible="modalVisible"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      :confirmLoading="modalLoading"
    >
      <a-form :model="formData" :rules="rules" ref="formRef">
        <a-form-item label="评论内容" name="content">
          <a-textarea v-model:value="formData.content" :rows="4" />
        </a-form-item>
        <a-form-item label="情感倾向" name="sentiment">
          <a-select v-model:value="formData.sentiment">
            <a-select-option value="positive">积极</a-select-option>
            <a-select-option value="neutral">中性</a-select-option>
            <a-select-option value="negative">消极</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import type { TableColumnsType } from 'ant-design-vue';
import axios from 'axios';

interface ReviewData {
  _id: string;
  user_id: string;
  movie_id: string;
  movie_title: string;
  username: string;
  content: string;
  sentiment: string;
  created_at: string;
}

export default defineComponent({
  name: 'ReviewManagement',
  setup() {
    const reviews = ref<ReviewData[]>([]);
    const loading = ref(false);
    const modalVisible = ref(false);
    const modalLoading = ref(false);
    const formRef = ref();
    const formData = ref({
      _id: '',
      content: '',
      sentiment: ''
    });

    const columns: TableColumnsType = [
      {
        title: '电影',
        dataIndex: 'movie_title',
        key: 'movie_title'
      },
      {
        title: '用户',
        dataIndex: 'username',
        key: 'username'
      },
      {
        title: '评论内容',
        dataIndex: 'content',
        key: 'content',
        ellipsis: true
      },
      {
        title: '情感倾向',
        key: 'sentiment'
      },
      {
        title: '发布时间',
        dataIndex: 'created_at',
        key: 'created_at',
        sorter: (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      },
      {
        title: '操作',
        key: 'action',
        width: 150
      }
    ];

    const rules = {
      content: [{ required: true, message: '请输入评论内容' }],
      sentiment: [{ required: true, message: '请选择情感倾向' }]
    };

    const fetchReviews = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/reviews/all');
        reviews.value = response.data;
      } catch (error) {
        message.error('获取评论数据失败');
      }
      loading.value = false;
    };

    const showEditModal = (record: ReviewData) => {
      formData.value = {
        _id: record._id,
        content: record.content,
        sentiment: record.sentiment
      };
      modalVisible.value = true;
    };

    const handleModalOk = async () => {
      try {
        await formRef.value.validate();
        modalLoading.value = true;

        await axios.put(`/api/reviews/${formData.value._id}`, {
          content: formData.value.content,
          sentiment: formData.value.sentiment
        });
        
        message.success('更新成功');
        modalVisible.value = false;
        fetchReviews();
      } catch (error) {
        message.error('更新失败');
      } finally {
        modalLoading.value = false;
      }
    };

    const handleModalCancel = () => {
      modalVisible.value = false;
    };

    const handleDelete = async (id: string) => {
      try {
        await axios.delete(`/api/reviews/${id}`);
        message.success('删除成功');
        fetchReviews();
      } catch (error) {
        message.error('删除失败');
      }
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
      columns,
      modalVisible,
      modalLoading,
      formRef,
      formData,
      rules,
      showEditModal,
      handleModalOk,
      handleModalCancel,
      handleDelete,
      getSentimentColor,
      getSentimentText
    };
  }
});
</script>

<style scoped>
.review-management {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

h2 {
  margin: 0;
}
</style> 