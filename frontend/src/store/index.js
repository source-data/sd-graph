import Vue from 'vue'
import Vuex from 'vuex'
import { byArticleId } from './by-article-id'
import { byFilters } from './by-filters'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byArticleId,
    byFilters
  },
  state: {
    snackMessage: "",
    snackColor: ""
  },
  getters: {},
  mutations: {
    setSnack (state, snackInfo) {
      state.snackMessage = snackInfo.message;
      state.snackColor = snackInfo.color
    }
  },
  actions: {},
})
