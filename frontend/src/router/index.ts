import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '../stores/user'
import { message } from 'ant-design-vue'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 导入新的页面组件
import Reviews from '../views/Reviews.vue'
import Favorites from '../views/Favorites.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MovieList from '../views/MovieList.vue'
import MovieDetail from '../views/MovieDetail.vue'
import Analysis from '../views/Analysis.vue'
import Admin from '../views/Admin.vue'
import Profile from '../views/Profile.vue'
import Activities from '../views/Activities.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'MovieList',
    component: MovieList
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/movie/:id',
    name: 'MovieDetail',
    component: MovieDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    //component: Admin,
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'reviews',
        name: 'review-analytics',
        component: () => import('../views/admin/ReviewAnalytics.vue')
      },
      {
        path: 'movies',
        name: 'movie-analytics',
        component: () => import('../views/admin/MovieAnalytics.vue')
      },
      {
        path: 'users',
        name: 'user-analytics',
        component: () => import('../views/admin/UserAnalytics.vue')
      },
      {
        path: 'movie-management',
        name: 'movie-management',
        component: () => import('../views/admin/MovieManagement.vue')
      },
      {
        path: 'review-management',
        name: 'review-management',
        component: () => import('../views/admin/ReviewManagement.vue')
      }
    ]
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: Favorites,
    meta: { requiresAuth: true }
  },
  {
    path: '/reviews',
    name: 'Reviews',
    component: Reviews,
    meta: { requiresAuth: true }
  },
  {
    path: '/activities',
    name: 'Activities',
    component: Activities,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  NProgress.start()
  const userStore = useUserStore()

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!userStore.isLoggedIn) {
      message.warning('请先登录')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    if (to.matched.some(record => record.meta.requiresAdmin) && !userStore.isAdmin) {
      message.error('无权访问')
      next('/')
      return
    }
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router 