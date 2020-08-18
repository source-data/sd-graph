import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import ArticleShow from '../components/highlights/article.vue'

Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/refereed_preprints',
    name: 'RefereedPreprints',
    component: Home
  },
  {
    path: '/covid19/by_hyp',
    name: 'Covid19ByHyp',
    component: Home
  },
  {
    path: '/covid19/automagic',
    name: 'Covid19Automagic',
    component: Home
  },
  {
    path: '/covid19/search',
    name: 'Covid19Search',
    component: Home
  },

  {
    path: '/doi/:doi(.*)',
    name: 'ArticleShow',
    component: ArticleShow,
  },

  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
