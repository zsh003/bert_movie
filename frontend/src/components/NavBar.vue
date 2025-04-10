<template>
  <a-layout-header class="header">
    <div class="logo">电影评论系统</div>
    <a-menu
      v-model:selectedKeys="selectedKeys"
      theme="dark"
      mode="horizontal"
      :style="{ lineHeight: '64px' }"
    >
      <a-menu-item key="home">
        <router-link to="/">首页</router-link>
      </a-menu-item>
      <template v-if="isLoggedIn">
        <a-menu-item key="activities">
          <router-link to="/activities">我的动态</router-link>
        </a-menu-item>
        <a-menu-item key="reviews">
          <router-link to="/reviews">我的评论</router-link>
        </a-menu-item>
        <a-menu-item key="favorites">
          <router-link to="/favorites">我的收藏</router-link>
        </a-menu-item>
        <a-menu-item key="logout" @click="handleLogout">
          退出登录
        </a-menu-item>
      </template>
      <template v-else>
        <a-menu-item key="login">
          <router-link to="/login">登录</router-link>
        </a-menu-item>
        <a-menu-item key="register">
          <router-link to="/register">注册</router-link>
        </a-menu-item>
      </template>
    </a-menu>
  </a-layout-header>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'

export default defineComponent({
  name: 'NavBar',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const selectedKeys = ref([route.name?.toLowerCase() || 'home'])

    const isLoggedIn = computed(() => {
      return !!localStorage.getItem('token')
    })

    const handleLogout = () => {
      localStorage.removeItem('token')
      message.success('已退出登录')
      router.push('/login')
    }

    return {
      selectedKeys,
      isLoggedIn,
      handleLogout
    }
  }
})
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
}

.logo {
  color: white;
  font-size: 20px;
  margin-right: 30px;
}

:deep(.ant-menu) {
  flex: 1;
}
</style> 