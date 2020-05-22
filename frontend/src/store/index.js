import Vue from 'vue'
import Vuex from 'vuex'
import byMethod from './by-method'
import byMol from './by-mol'
import byHyp from './by-hyp'
import highlights from './highlights'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byMethod,
    byHyp,
    byMol,
    highlights,
  },
  state: {
  },
  mutations: {
  },
  actions: {
  },
})
