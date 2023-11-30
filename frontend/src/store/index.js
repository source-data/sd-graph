import Vue from 'vue'
import Vuex from 'vuex'
import httpClient from '../lib/http'
import { byReviewingService } from './by-reviewing-service'
import highlights from './highlights'
import fulltextSearch from './fulltext-search'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    byReviewingService,
    highlights,
    fulltextSearch
  },
  state: {
    stats: {
      autoannotated_preprints: undefined,
      preprints: undefined,
      refereed_preprints: undefined,
    },
    loadingRecords: false,
  },
  getters: {
    db_stats(state) {
      return state.stats
    },

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
            autoannotated_preprints: resp.autoannotated_preprints,
            preprints: resp.preprints,
            refereed_preprints: resp.refereed_preprints,
            num_reviews: resp.num_reviews,
            num_docmaps: resp.num_docmaps,
            last_updated: resp.last_updated,
          }
          commit('setStats', stats)
        })
        .finally(() => {
          commit('setNotLoading')
        })
    }
  },
})
