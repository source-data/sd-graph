import Vue from 'vue'
import Vuex from 'vuex'
import byMethod from './by-method'
import highlights from './highlights'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byMethod,
    highlights,
  },
  state: {
  },
  mutations: {
  },
  actions: {
  },
})
