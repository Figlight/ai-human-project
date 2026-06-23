import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/chat'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/tourist/LoginView.vue'),
    meta: { title: '账号登录', layout: 'auth' }
  },
  {
    path: '/register',
    name: 'AdminRegister',
    component: () => import('../views/tourist/AdminRegisterView.vue'),
    meta: { title: '管理员注册', layout: 'auth' }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/tourist/ChatView.vue'),
    meta: { title: 'AI导游对话', layout: 'tourist' }
  },
  {
    path: '/attractions',
    name: 'Attractions',
    component: () => import('../views/tourist/AttractionsView.vue'),
    meta: { title: '景点与路线', layout: 'tourist' }
  },
  {
    path: '/conversations',
    name: 'Conversations',
    component: () => import('../views/tourist/ConversationsView.vue'),
    meta: { title: '历史记录', layout: 'tourist' }
  },
  {
    path: '/admin',
    name: 'Dashboard',
    component: () => import('../views/admin/DashboardView.vue'),
    meta: { title: '数据大屏', layout: 'admin' }
  },
  {
    path: '/admin/knowledge',
    name: 'Knowledge',
    component: () => import('../views/admin/KnowledgeView.vue'),
    meta: { title: '知识库管理', layout: 'admin' }
  },
  {
    path: '/admin/digital-human',
    name: 'DigitalHuman',
    component: () => import('../views/admin/DigitalHumanView.vue'),
    meta: { title: '数字人配置', layout: 'admin' }
  },
  {
    path: '/admin/analytics',
    name: 'Analytics',
    component: () => import('../views/admin/AnalyticsView.vue'),
    meta: { title: '游客洞察', layout: 'admin' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '404', layout: 'tourist' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const adminToken = sessionStorage.getItem('admin_token')
  const adminUserStr = sessionStorage.getItem('admin_user')
  const adminUser = adminUserStr ? JSON.parse(adminUserStr) : null

  const userToken = sessionStorage.getItem('user_token')
  const userUserStr = sessionStorage.getItem('user_user')
  const userUser = userUserStr ? JSON.parse(userUserStr) : null

  // Bypass login and admin register pages
  if (to.name === 'Login' || to.name === 'AdminRegister') {
    return next()
  }

  // Admin routes: require admin_token & admin user role
  if (to.path.startsWith('/admin')) {
    if (!adminToken || !adminUser || adminUser.role !== 'admin') {
      return next('/login')
    }
    return next()
  }

  // User/Tourist routes: require user_token
  if (to.path === '/chat' || to.path === '/attractions' || to.path === '/conversations') {
    if (!userToken || !userUser) {
      return next('/login')
    }
    return next()
  }

  next()
})

export default router
