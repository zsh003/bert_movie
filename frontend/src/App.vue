<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import {
  HomeOutlined,
  BarChartOutlined,
  UserOutlined,
  LoginOutlined,
  LogoutOutlined,
  DashboardOutlined,
  HeartOutlined,
  CommentOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const selectedKeys = ref([route.name as string])
const collapsed = ref(false)

// 菜单配置
const menus = computed(() => {
  const baseMenus = [
    {
      key: 'MovieList',
      icon: HomeOutlined,
      title: '电影列表',
      path: '/',
      requiresAuth: true
    }
  ]

  // 已登录用户菜单
  if (userStore.isLoggedIn) {
    if (userStore.isAdmin) {
      // 管理员菜单
      baseMenus.push(
        {
          key: 'Analysis',
          icon: BarChartOutlined,
          title: '数据分析',
          path: '/analysis'
        },
        {
          key: 'Admin',
          icon: DashboardOutlined,
          title: '管理控制台',
          path: '/admin'
        }
      )
    } else {
      // 普通用户菜单
      baseMenus.push(
        {
          key: 'Favorites',
          icon: HeartOutlined,
          title: '我的收藏',
          path: '/favorites'
        },
        {
          key: 'MyReviews',
          icon: CommentOutlined,
          title: '我的评论',
          path: '/reviews'
        }
      )
    }
  } else {
    // 未登录用户菜单
    baseMenus.push({
      key: 'Login',
      icon: LoginOutlined,
      title: '登录',
      path: '/login'
    })
  }

  return baseMenus
})

// 用户下拉菜单项
const userMenuItems = computed(() => {
  const items = [
    {
      key: 'profile',
      icon: UserOutlined,
      title: '个人信息',
      onClick: () => router.push('/profile')
    },
    {
      key: 'settings',
      icon: SettingOutlined,
      title: '账号设置',
      onClick: () => router.push('/profile?tab=settings')
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      icon: LogoutOutlined,
      title: '退出登录',
      onClick: handleLogout
    }
  ]
  return items
})

// 监听路由变化
watch(
  () => route.name,
  (name) => {
    if (name) {
      selectedKeys.value = [name]
    }
  }
)

const handleMenuClick = (menu) => {
  router.push(menu.key === 'MovieList' ? '/' : `/${menu.key.toLowerCase()}`)
}

const handleLogout = async () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <a-layout class="layout">
    <a-layout-header class="header">
      <div class="logo">基于BERT的中文电影评论情感分析系统</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="horizontal"
        class="menu"
      >
        <a-menu-item v-for="menu in menus" :key="menu.key">
          <router-link :to="menu.path">
            <component :is="menu.icon" />
            <span>{{ menu.title }}</span>
          </router-link>
        </a-menu-item>
      </a-menu>
      <div class="header-right" v-if="userStore.isLoggedIn">
        <a-dropdown>
          <a class="user-dropdown" @click.prevent>
            <a-avatar :src="userStore.user?.avatar">
              <template #icon><UserOutlined /></template>
            </a-avatar>
            <span class="username">{{ userStore.user?.username }}</span>
          </a>
          <template #overlay>
            <a-menu>
              <template v-for="item in userMenuItems" :key="item.key">
                <a-menu-divider v-if="item.type === 'divider'" />
                <a-menu-item v-else @click="item.onClick">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </a-menu-item>
              </template>
            </a-menu>
          </template>
        </a-dropdown>
      </div>
    </a-layout-header>

    <a-layout-content>
      <div class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </a-layout-content>

    <a-layout-footer class="footer">
      基于BERT的中文电影评论情感分析系统 ©2024
    </a-layout-footer>
  </a-layout>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}

#app {
  height: 100vh;
}

.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: #001529;
  position: fixed;
  width: 100%;
  z-index: 1000;
}

.logo {
  color: white;
  font-size: 20px;
  font-weight: bold;
  margin-right: 48px;
  white-space: nowrap;
}

.menu {
  flex: 1;
  min-width: 0;
}

.header-right {
  margin-left: auto;
  white-space: nowrap;
}

.user-dropdown {
  color: white;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  color: white;
}

.main-content {
  padding: 88px 24px 24px;
  min-height: calc(100vh - 64px - 70px);
  background: #f0f2f5;
}

.footer {
  text-align: center;
  padding: 24px;
  background: #f0f2f5;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 覆盖 Ant Design Vue 的一些默认样式 */
.ant-layout-header {
  height: 64px;
  line-height: 64px;
  padding: 0 24px;
}

.ant-menu-horizontal {
  border-bottom: none;
}

.ant-menu-horizontal > .ant-menu-item,
.ant-menu-horizontal > .ant-menu-submenu {
  height: 64px;
  line-height: 64px;
  border-bottom: none;
}

.ant-menu-horizontal > .ant-menu-item:hover {
  border-bottom: 2px solid #1890ff;
}

.ant-menu-horizontal > .ant-menu-item-selected {
  border-bottom: 2px solid #1890ff;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .logo {
    margin-right: 24px;
  }

  .username {
    display: none;
  }

  .main-content {
    padding: 88px 12px 12px;
  }
}
</style>
