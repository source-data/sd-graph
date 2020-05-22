import Vue from 'vue'
import Vuex from 'vuex'
import byMethod from './by-method'
import byHyp from './by-hyp'
import highlights from './highlights'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byMethod,
    byHyp,
    highlights,
  },
  state: {
  },
  mutations: {
  },
  actions: {
  },
})
