import Vue from 'vue'
import Vuex from 'vuex'
import { byFilters } from './by-filters'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
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
