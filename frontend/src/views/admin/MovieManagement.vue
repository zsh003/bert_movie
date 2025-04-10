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
      :pagination="{ pageSize: 10 }"
      rowKey="_id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'poster'">
          <img :src="record.poster" alt="海报" style="width: 50px; height: 70px; object-fit: cover;" />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button type="link" @click="showEditModal(record)">编辑</a-button>
            <a-popconfirm
              title="确定要删除这部电影吗？"
              @confirm="handleDelete(record._id)"
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
          <a-input v-model:value="formData.poster" />
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
import type { TableColumnsType } from 'ant-design-vue';
import axios from 'axios';

interface MovieData {
  _id: string;
  title: string;
  poster: string;
  director: string;
  actors: string;
  genre: string;
  release_date: string;
  description: string;
}

export default defineComponent({
  name: 'MovieManagement',
  setup() {
    const movies = ref<MovieData[]>([]);
    const loading = ref(false);
    const modalVisible = ref(false);
    const modalLoading = ref(false);
    const modalTitle = ref('添加电影');
    const formRef = ref();
    const formData = ref({
      _id: '',
      title: '',
      poster: '',
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
        title: '电影名称',
        dataIndex: 'title',
        key: 'title'
      },
      {
        title: '导演',
        dataIndex: 'director',
        key: 'director'
      },
      {
        title: '主演',
        dataIndex: 'actors',
        key: 'actors'
      },
      {
        title: '类型',
        dataIndex: 'genre',
        key: 'genre'
      },
      {
        title: '上映日期',
        dataIndex: 'release_date',
        key: 'release_date'
      },
      {
        title: '操作',
        key: 'action',
        width: 150
      }
    ];

    const rules = {
      title: [{ required: true, message: '请输入电影名称' }],
      poster: [{ required: true, message: '请输入海报URL' }],
      director: [{ required: true, message: '请输入导演' }],
      actors: [{ required: true, message: '请输入主演' }],
      genre: [{ required: true, message: '请输入类型' }],
      release_date: [{ required: true, message: '请选择上映日期' }],
      description: [{ required: true, message: '请输入简介' }]
    };

    const fetchMovies = async () => {
      loading.value = true;
      try {
        const response = await axios.get('/api/movies');
        movies.value = response.data;
      } catch (error) {
        message.error('获取电影数据失败');
      }
      loading.value = false;
    };

    const showAddModal = () => {
      modalTitle.value = '添加电影';
      formData.value = {
        _id: '',
        title: '',
        poster: '',
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
      formData.value = { ...record };
      modalVisible.value = true;
    };

    const handleModalOk = async () => {
      try {
        await formRef.value.validate();
        modalLoading.value = true;

        if (formData.value._id) {
          // 编辑
          await axios.put(`/api/movies/${formData.value._id}`, formData.value);
          message.success('更新成功');
        } else {
          // 添加
          await axios.post('/api/movies', formData.value);
          message.success('添加成功');
        }

        modalVisible.value = false;
        fetchMovies();
      } catch (error) {
        message.error('操作失败');
      } finally {
        modalLoading.value = false;
      }
    };

    const handleModalCancel = () => {
      modalVisible.value = false;
    };

    const handleDelete = async (id: string) => {
      try {
        await axios.delete(`/api/movies/${id}`);
        message.success('删除成功');
        fetchMovies();
      } catch (error) {
        message.error('删除失败');
      }
    };

    onMounted(() => {
      fetchMovies();
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
      showAddModal,
      showEditModal,
      handleModalOk,
      handleModalCancel,
      handleDelete
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