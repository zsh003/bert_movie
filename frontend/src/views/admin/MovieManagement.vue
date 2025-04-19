<template>
  <div class="movie-management">
    <div class="page-header">
      <h2>电影数据管理</h2>
      <a-button type="primary" @click="showAddModal">添加电影</a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="movies"
      :loading="loading"
      :pagination="{
        current: current,
        pageSize: pageSize,
        total: total,
        showSizeChanger: true,
        pageSizeOptions: ['10', '20', '50', '100'],
        showTotal: (total) => `共 ${total} 条记录`
      }"
      @change="handleTableChange"
      rowKey="movie_id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'poster'">
          <img 
            :src="record.img && record.img.content ? 'data:image/webp;base64,' + record.img.content : ''" 
            alt="海报" 
            style="width: 50px; height: 70px; object-fit: cover;" 
          />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="showEditModal(record)">编辑</a-button>
            <a-popconfirm
              title="确定要删除这部电影吗？"
              @confirm="handleDelete(record.movie_id)"
            >
              <a-button type="link" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 添加/编辑电影的模态框 -->
    <a-modal
      :title="modalTitle"
      :visible="modalVisible"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
      :confirmLoading="modalLoading"
    >
      <a-form :model="formData" :rules="rules" ref="formRef">
        <a-form-item label="电影名称" name="title">
          <a-input v-model:value="formData.title" />
        </a-form-item>
        <a-form-item label="海报URL" name="poster">
          <a-input v-model:value="formData.img" />
        </a-form-item>
        <a-form-item label="导演" name="director">
          <a-input v-model:value="formData.director" />
        </a-form-item>
        <a-form-item label="主演" name="actors">
          <a-input v-model:value="formData.actors" />
        </a-form-item>
        <a-form-item label="类型" name="genre">
          <a-input v-model:value="formData.genre" />
        </a-form-item>
        <a-form-item label="上映日期" name="release_date">
          <a-date-picker v-model:value="formData.release_date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="简介" name="description">
          <a-textarea v-model:value="formData.description" :rows="4" />
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

interface MovieData {
  movie_id: number;
  title: string;
  img: any;
  director?: string;
  actors?: string;
  genre: string;
  release_date?: string;
  description: string;
  url_film?: string;
  source?: string;
}

export default defineComponent({
  name: 'MovieManagement',
  setup() {
    const userStore = useUserStore();
    const movies = ref<MovieData[]>([]);
    const loading = ref(false);
    const modalVisible = ref(false);
    const modalLoading = ref(false);
    const modalTitle = ref('添加电影');
    const formRef = ref();
    
    // 分页相关状态
    const current = ref(1);
    const pageSize = ref(10);
    const total = ref(0);
    
    const formData = ref({
      movie_id: 0,
      title: '',
      img: '',
      director: '',
      actors: '',
      genre: '',
      release_date: '',
      description: ''
    });

    const columns: TableColumnsType = [
      {
        title: '海报',
        key: 'poster',
        width: 80
      },
      {
        title: '电影ID',
        dataIndex: 'movie_id',
        key: 'movie_id'
      },
      {
        title: '电影名称',
        dataIndex: 'title',
        key: 'title'
      },
      {
        title: '类型',
        dataIndex: 'genre',
        key: 'genre'
      },
      {
        title: '简介',
        dataIndex: 'description',
        key: 'description',
        ellipsis: true
      },
      {
        title: '操作',
        key: 'action',
        width: 150
      }
    ];

    const rules = {
      title: [{ required: true, message: '请输入电影名称' }],
      img: [{ required: true, message: '请输入海报URL' }],
      genre: [{ required: true, message: '请输入类型' }],
      description: [{ required: true, message: '请输入简介' }]
    };

    const fetchMovies = async (page = 1, size = 10) => {
      loading.value = true;
      try {
        const skip = (page - 1) * size;
        const response = await axios.get(`http://localhost:8000/api/movies`, {
          params: {
            skip: skip,
            limit: size
          },
          headers: {
            'Authorization': `Bearer ${userStore.token}`
          }
        });
        
        // 直接使用返回的数组
        movies.value = response.data;
        
        // 获取总数（这里假设有100条，理想情况应从后端获取）
        // 后续可以通过单独的API来获取总数
        total.value = 100;
      } catch (error) {
        console.error('获取电影数据失败:', error);
        message.error('获取电影数据失败');
      }
      loading.value = false;
    };
    
    // 处理表格分页、排序、筛选变化
    const handleTableChange = (pagination: TablePaginationConfig) => {
      current.value = pagination.current || 1;
      pageSize.value = pagination.pageSize || 10;
      fetchMovies(current.value, pageSize.value);
    };

    const showAddModal = () => {
      modalTitle.value = '添加电影';
      formData.value = {
        movie_id: 0,
        title: '',
        img: '',
        director: '',
        actors: '',
        genre: '',
        release_date: '',
        description: ''
      };
      modalVisible.value = true;
    };

    const showEditModal = (record: MovieData) => {
      modalTitle.value = '编辑电影';
      formData.value = { 
        movie_id: record.movie_id,
        title: record.title,
        img: record.img?.content || '',
        director: record.director || '',
        actors: record.actors || '',
        genre: record.genre,
        release_date: record.release_date || '',
        description: record.description
      };
      modalVisible.value = true;
    };

    const handleModalOk = async () => {
      try {
        await formRef.value.validate();
        modalLoading.value = true;

        if (formData.value.movie_id) {
          // 编辑
          await axios.put(`http://localhost:8000/api/movies/${formData.value.movie_id}`, formData.value, {
            headers: {
              'Authorization': `Bearer ${userStore.token}`
            }
          });
          message.success('更新成功');
        } else {
          // 添加
          await axios.post('http://localhost:8000/api/movies', formData.value, {
            headers: {
              'Authorization': `Bearer ${userStore.token}`
            }
          });
          message.success('添加成功');
        }

        modalVisible.value = false;
        fetchMovies(current.value, pageSize.value); // 刷新当前页数据
      } catch (error) {
        console.error('操作失败:', error);
        message.error('操作失败');
      } finally {
        modalLoading.value = false;
      }
    };

    const handleModalCancel = () => {
      modalVisible.value = false;
    };

    const handleDelete = async (id: number) => {
      try {
        await axios.delete(`http://localhost:8000/api/movies/${id}`, {
          headers: {
            'Authorization': `Bearer ${userStore.token}`
          }
        });
        message.success('删除成功');
        
        // 如果当前页只有一条数据且不是第一页，删除后跳转到上一页
        if (movies.value.length === 1 && current.value > 1) {
          current.value -= 1;
        }
        fetchMovies(current.value, pageSize.value);
      } catch (error) {
        console.error('删除失败:', error);
        message.error('删除失败');
      }
    };

    onMounted(() => {
      fetchMovies(current.value, pageSize.value);
    });

    return {
      movies,
      loading,
      columns,
      modalVisible,
      modalLoading,
      modalTitle,
      formRef,
      formData,
      rules,
      current,
      pageSize,
      total,
      showAddModal,
      showEditModal,
      handleModalOk,
      handleModalCancel,
      handleDelete,
      handleTableChange
    };
  }
});
</script>

<style scoped>
.movie-management {
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