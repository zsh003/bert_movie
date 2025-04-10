<template>
  <a-layout class="admin-layout">
    <a-layout-sider width="200" class="admin-sider">
      <div class="logo">
        <h1>管理后台</h1>
      </div>
      <a-menu
        mode="inline"
        v-model:selectedKeys="selectedKeys"
        :style="{ height: '100%', borderRight: 0 }"
      >
        <a-menu-item key="review-analytics" @click="$router.push('/admin/reviews')">
          <template #icon><bar-chart-outlined /></template>
          影评分析
        </a-menu-item>
        <a-menu-item key="movie-analytics" @click="$router.push('/admin/movies')">
          <template #icon><line-chart-outlined /></template>
          电影分析
        </a-menu-item>
        <a-menu-item key="user-analytics" @click="$router.push('/admin/users')">
          <template #icon><user-outlined /></template>
          用户分析
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="admin-header">
        <div class="header-right">
          <a-dropdown>
            <a class="ant-dropdown-link" @click.prevent>
              {{ userStore.username }}
              <down-outlined />
            </a>
            <template #overlay>
              <a-menu>
                <a-menu-item key="0" @click="handleLogout">
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout-content class="admin-content">
        <router-view></router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import {
  BarChartOutlined,
  LineChartOutlined,
  UserOutlined,
  DownOutlined
} from '@ant-design/icons-vue';

export default defineComponent({
  name: 'AdminLayout',
  components: {
    BarChartOutlined,
    LineChartOutlined,
    UserOutlined,
    DownOutlined
  },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const userStore = useUserStore();

    const selectedKeys = ref<string[]>([route.name as string]);

    const handleLogout = async () => {
      await userStore.logout();
      router.push('/login');
    };

    return {
      selectedKeys,
      userStore,
      handleLogout
    };
  }
});
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.admin-sider {
  background: #fff;
}

.logo {
  height: 64px;
  padding: 16px;
  text-align: center;
  background: #001529;
}

.logo h1 {
  color: #fff;
  margin: 0;
  font-size: 20px;
  line-height: 32px;
}

.admin-header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-right {
  display: flex;
  align-items: center;
}

.ant-dropdown-link {
  color: rgba(0, 0, 0, 0.85);
  cursor: pointer;
}

.admin-content {
  margin: 0;
  min-height: 280px;
  background: #fff;
}
</style> 