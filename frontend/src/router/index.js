import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'


Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    redirect: '/refereed-preprints/review-commons',
  },
  {
    path: '/:collection/:service',
    name: 'Home',
    component: Home,
    props: true,
  },
  {
    path: '/doi/:doi(.*)',
    name: 'ArticleShow',
    component: () => import(/* webpackChunkName: "ArticleShow" */ '../components/highlights/article.vue')
  },

  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/*',
    name: 'NotFound',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "NotFound" */ '../views/NotFound.vue')
  },
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
