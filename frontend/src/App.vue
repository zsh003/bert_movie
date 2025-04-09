<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const selectedKeys = ref(['movies'])

// 根据路由更新选中的菜单项
watch(
  () => route.path,
  (path) => {
    if (path === '/') {
      selectedKeys.value = ['movies']
    } else if (path === '/analysis') {
      selectedKeys.value = ['analysis']
    }
  },
  { immediate: true }
)
</script>

<template>
  <a-layout class="layout">
    <a-layout-header>
      <div class="logo">电影分析系统</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="horizontal"
        :style="{ lineHeight: '64px' }"
      >
        <a-menu-item key="movies">
          <router-link to="/">电影列表</router-link>
        </a-menu-item>
        <a-menu-item key="analysis">
          <router-link to="/analysis">数据分析</router-link>
        </a-menu-item>
      </a-menu>
    </a-layout-header>
    <a-layout-content>
      <router-view/>
    </a-layout-content>
    <a-layout-footer style="text-align: center">
      电影评论情感分析系统 ©2024
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

.ant-layout-header {
  display: flex;
  align-items: center;
}

.ant-layout-content {
  background: #fff;
  min-height: calc(100vh - 64px - 70px);
}

.ant-layout-footer {
  padding: 24px;
}
</style>
