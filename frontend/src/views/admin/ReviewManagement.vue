<template>
  <div class="review-management">
    <div class="page-header">
      <h2>影评数据管理</h2>
    </div>

    <a-table
      :columns="columns"
      :data-source="reviews"
      :loading="loading"
      :pagination="{
        current: current,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        pageSizeOptions: ['10', '20', '50'],
        showTotal: (total) => `共 ${total} 条记录`
      }"
      @change="handleTableChange"
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
import type { TableColumnsType, TablePaginationConfig } from 'ant-design-vue';
import axios from 'axios';
import { useUserStore } from '../../stores/user'

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
    const userStore = useUserStore();
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
    
    // 分页相关状态
    const current = ref(1);
    const pageSize = ref(10);
    const total = ref(0);

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

    const fetchReviews = async (page = 1, size = 10) => {
      loading.value = true;
      try {
        // 使用后端reviews/all接口获取数据
        const response = await axios.get('http://localhost:8000/api/reviews/all', {
          params: {
            skip: (page - 1) * size,
            limit: size
          },
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        if (response.data && response.data.data) {
          reviews.value = response.data.data;
          total.value = response.data.total || 0;
        } else {
          // 如果接口不返回预期格式，尝试直接使用数据
          reviews.value = Array.isArray(response.data) ? response.data : [];
          total.value = reviews.value.length;
        }
      } catch (error) {
        console.error('获取评论数据失败:', error);
        message.error('获取评论数据失败');
        
        // 如果接口失败，尝试使用模拟数据（仅用于调试）
        reviews.value = [];
        total.value = 0;
      }
      loading.value = false;
    };
    
    // 处理表格分页变化
    const handleTableChange = (pagination: TablePaginationConfig) => {
      current.value = pagination.current || 1;
      pageSize.value = pagination.pageSize || 10;
      fetchReviews(current.value, pageSize.value);
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

        await axios.put(`http://localhost:8000/api/reviews/${formData.value._id}`, {
          content: formData.value.content,
          sentiment: formData.value.sentiment
        }, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        
        message.success('更新成功');
        modalVisible.value = false;
        fetchReviews(current.value, pageSize.value);
      } catch (error) {
        console.error('更新失败:', error);
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
        await axios.delete(`http://localhost:8000/api/reviews/${id}`, {
          headers: {
            Authorization: `Bearer ${userStore.token}`
          }
        });
        message.success('删除成功');
        
        // 如果当前页只有一条数据且不是第一页，删除后跳转到上一页
        if (reviews.value.length === 1 && current.value > 1) {
          current.value -= 1;
        }
        fetchReviews(current.value, pageSize.value);
      } catch (error) {
        console.error('删除失败:', error);
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
      fetchReviews(current.value, pageSize.value);
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
      current,
      pageSize,
      total,
      showEditModal,
      handleModalOk,
      handleModalCancel,
      handleDelete,
      handleTableChange,
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