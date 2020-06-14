import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    currentRecordId: null,
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      //return Object.values(state.records).slice().sort((a, b) => a.item_name.toLowerCase().localeCompare(b.item_name.toLowerCase()))
      return Object.values(state.records)
    },
    currentRecord (state) {
      return state.records//[state.currentRecordId]
    },
    isLoaded (state) {
      return state.loadComplete
    }
  },
  mutations: {
    /* *************************************************************************
    * RECORDS
    */
   addRecords (state, records) {
      // need to sort and truncate records here
      const sorted = Object.values(records).slice().sort((a, b) => b.score - a.score)
      const top10 = sorted.slice(0, 10)
      state.records = {papers: top10}
    },
    /* *************************************************************************
    * NAVIGATION
    */
   setIsLoading (state) {
      state.loadingRecords = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
    },
    setLoadComplete (state) {
      state.loadComplete = true
    },
    closeRecordView (state) {
      state.currentRecordId = null
    },
  },
  actions: {
    search({ commit }, query) {
      commit('setIsLoading')
      const url = '/api/v1/search/'
      // return httpClient.post(url, {query: query}) 
      return httpClient.get(url, {
          params: {
              query: query
          }
      })
        .then((response) => {
          const records = response.data
          commit('addRecords', records)
        })
        .finally(() => {
          commit('setNotLoading'),
          commit('setLoadComplete')
        })
    },
  },
}
