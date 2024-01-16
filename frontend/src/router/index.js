import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import AdvancedSearch from '../views/AdvancedSearch.vue'


Vue.use(VueRouter)


const routes = [
  {
    path: '/',
    redirect: '/refereed-preprints',
  },
  {
    path: '/doi/:doi(.*)',
    name: 'ArticleShowByDoi',
    component: () => import(/* webpackChunkName: "ArticleShow" */ '../components/highlights/article.vue')
  },
  {
    path: '/p/:slug(.*)',
    name: 'ArticleShowBySlug',
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
    path: '/contact',
    name: 'Contact',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/Contact.vue')
  },
  {
    path: '/refereed-preprints',
    name: 'Home',
    component: Home,
    props: true,
  },
  {
    path: '/advanced-search',
    name: 'AdvancedSearch',
    component: AdvancedSearch,
    props: true,
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
