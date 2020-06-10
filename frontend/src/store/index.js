import Vue from 'vue'
import Vuex from 'vuex'
import httpClient from '../lib/http'
import byAutomagic from './by-automagic'
import byMethod from './by-method'
import byMol from './by-mol'
import byHyp from './by-hyp'
import byReviewingService from './by-reviewing-service'
import highlights from './highlights'
import fulltextSearch from './fulltext-search'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byAutomagic,
    byMethod,
    byHyp,
    byMol,
    byReviewingService,
    highlights,
    fulltextSearch
  },
  state: {
    journalNameDict: {
      biorxiv: 'bioRxiv', 
      medrxiv: 'medRxiv',
      'review commons': 'Review Commons',
      elife: 'eLife',
      'embo press': 'EMBO Press',
    },
    stats: {
      total_preprints: undefined,
      sd_annotated: undefined,
      ai_annotated: undefined,
      total_nodes: undefined,
      total_rel: undefined
    },
    loadingRecords: false,
  },
  getters: {
    db_stats(state) {
      return state.stats
    },
    journalName: (state) => (id) => { return state.journalNameDict[id.toLowerCase()] }
  },
  mutations: {
    setStats (state, stats) {
      state.stats = stats
    },
    setIsLoading (state) {
      state.loadingRecords = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
    },
  },
  actions: {
    statsFromFlask ({ commit }) {
      return httpClient.get('/api/v1/stats')
        .then((response) => {
          const resp = response.data[0]
          const stats = {
            total_preprints: resp.N_jats,
            sd_annotated: resp.N_sdapi,
            ai_annotated: resp.N_eeb,
            total_nodes: resp.N_nodes,
            total_rel: resp.N_rel
          }
          commit('setStats', stats)
        })
        .finally(() => {
          commit('setNotLoading')
        })
    }
  },
})
