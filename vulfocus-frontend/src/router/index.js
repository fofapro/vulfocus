import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: false
  },
  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      affix: true,
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: '首页', icon: 'dashboard' }
    }]
  },
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/index',
    children: [
      {
        path: 'index',
        component: () => import('@/views/profile/index'),
        name: 'Profile',
        meta: { title: '用户', icon: 'user', noCache: true }
      }
    ]
  },
  {
    path: '/userrank',
    component: Layout,
    redirect: '/userrank',
    children: [{
      path: 'list',
      affix: true,
      name: 'list',
      component: () => import('@/views/rank/index'),
      meta: { title: '积分总榜', icon: 'form' }
    }]
  },
  {
    path: '/time',
    component: Layout,
    redirect: '/time',
    children: [{
      path: 'time',
      affix: true,
      name: 'list',
      hidden: true,
      component: () => import('@/views/time/index'),
      meta: { title: '场景模式', icon: 'form' }
    }]
  },
  {
    path: '/',
    component: Layout,
    redirect: '/',
    children: [{
      path: '/scene/list',
      name: 'List',
      component: () => import('@/views/scene/list'),
      meta: { title: '场景', icon: 'table', noCache: true }
    }]
  },
  {
    path: '/',
    component: Layout,
    redirect: '/',
    meta: {title: "场景模式", icon: 'form'},
    hidden: true,
    children: [
      {
        path: '/scene/index',
        component: () => import('@/views/scene/index'),
        name: 'Index',
        hidden: true,
        meta: { title: '场景', icon: 'table', noCache: true }
      },]
  },

]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export const asyncRoutes = [
  {
    // 镜像管理
    path: '/image',
    component: Layout,
    redirect: '/image',
    meta: {role: ['admin'],title: "镜像管理", icon: 'docker'},
    children: [{
      path: 'image',
      affix: true,
      name: 'image',
      component: () => import('@/views/image/index'),
      meta: { title: '镜像管理', icon: 'docker' , role: ['admin']}
    },{
        path: 'images',
        affix: true,
        name: 'images',
        component: () => import("@/views/manager/images"),
        meta: { title: '靶场管理', icon: 'bug' , role: ['admin']}
      }]
  },
  {
    // 环境编排管理
    path: '/layout',
    component: Layout,
    redirect: '/layout',
    meta: {role: ['admin'], title: "场景管理", icon: "barrage_fill"},
    children: [{
      path: 'network',
      affix: true,
      name: 'network',
      component: () => import('@/views/network/index'),
      meta: { title: '网卡管理', icon: 'tree' , role: ['admin']}
    },{
      path: 'manager',
      affix: true,
      name: 'manager',
      component: () => import('@/views/layout/manager'),
      meta: { title: '环境编排管理', icon: 'barrage_fill' , role: ['admin']}
    },
      {
      path: 'index',
      affix: true,
      name: 'index',
      hidden: true,
      component: () => import('@/views/layout/index'),
      meta: { title: '创建', icon: 'barrage_fill' , role: ['admin']}
    },
    {
        path: 'timetemp',
        affix: true,
        name: 'timetemp',
        component: () => import("@/views/manager/timetemp"),
        meta: { title: '计时模版管理', icon: 'setting' , role: ['admin']}
    },
    ]
  },
  {
    // 账户管理
    path: '/manager',
    component: Layout,
    redirect: '/manager',
    meta: {role: ['admin'],title: "系统管理", icon: 'setting'},
    children: [
      {
        path: 'user',
        affix: true,
        name: 'user',
        component: () => import("@/views/manager/user"),
        meta: { title: '用户管理', icon: 'user' , role: ['admin']}
      },
      {
        path: 'log',
        affix: true,
        name: 'log',
        component: () => import("@/views/manager/log"),
        meta: { title: '日志管理', icon: 'log' , role: ['admin']}
      },
      {
        path: 'setting',
        component: () => import('@/views/manager/setting'),
        name: 'setting',
        meta: { title: '系统配置', icon: 'setting', noCache: true }
      },

    ]
  },
  { path: '*', redirect: '/404', hidden: true }
]


export default router
