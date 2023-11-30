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
    path: '/search',
    name: 'Search',
    component: () => import(/* webpackChunkName: "Search" */ '../views/Search.vue')
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
    path: '/for-developers',
    name: 'For developers',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/ForDevelopers.vue')
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
    path: '/:collection/:service',
    name: 'Home',
    component: Home,
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

let _lastVisitedReviewingService = undefined
router.beforeEach((to, _, next) => {
  /* ***************************************************************************
    Tricky business logic!
    We want to have custom subroutes for each reviewing service inside of the
    `refereed-preprints` collection. At the same time we want that the app
    remembers the last visted reviewing service (defaulting to review commons)
  */
  if (to.path.includes('refereed-preprints')) {
    if (to.params.service) {
      _lastVisitedReviewingService = to.params.service
      return next()
    }
    else {
      // remeber the last visited review service or default to review-commons
      let serviceName = undefined
      if (_lastVisitedReviewingService) {
        serviceName = _lastVisitedReviewingService
      } else {
        serviceName = 'review-commons'
      }
      return next(`/refereed-preprints/${serviceName}`)
    }
  }

  return next()
})


export default router
