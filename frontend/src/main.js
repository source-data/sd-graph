import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import VueMeta from 'vue-meta'
import vuetify from './plugins/vuetify';
import './scss/main.scss'
import i18n from './i18n'

Vue.use(VueMeta)

Vue.config.productionTip = false

const app = new Vue({
  i18n,
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

const shouldTriggerUpdate = ["byFilters/setReviewedBys", "byFilters/setQuery", "byFilters/setSortedBy", 
                             "byFilters/setSortedOrder", "byFilters/setCurrentPage", "byFilters/setPublishedIn"];

app.$store.subscribe((mutation) => {
  if (shouldTriggerUpdate.includes(mutation.type)) {
    // Reset pagination if we are not just trying to get to another page
    const shouldResetPagination = mutation.type !== "byFilters/setCurrentPage"
    app.$vuetify.goTo(0);
    app.$store.dispatch('byFilters/updateRecords', shouldResetPagination);
  }
})