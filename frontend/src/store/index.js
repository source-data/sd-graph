import Vue from 'vue'
import Vuex from 'vuex'
import byAutomagic from './by-automagic'
import byMethod from './by-method'
import byMol from './by-mol'
import byHyp from './by-hyp'
import highlights from './highlights'
import fulltextSearch from './fulltext-search'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byAutomagic,
    byMethod,
    byHyp,
    byMol,
    highlights,
    fulltextSearch
  },
  state: {
  },
  mutations: {
  },
  actions: {
  },
})
