import Vue from 'vue'
import Vuex from 'vuex'
import { byFilters } from './by-filters'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byFilters
  },
  state: {
    loadingRecords: false,
  },
  getters: {

  },
  mutations: {
    setIsLoading (state) {
      state.loadingRecords = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
    },
  },
  actions: {
  },
})
