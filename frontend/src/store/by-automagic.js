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
      return Object.values(state.records)
    },
    currentRecord (state) {
      return state.records
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
      state.records = records
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
    getAll ({ commit }) {
      commit('setIsLoading')
      const url = '/api/v1/automagic/'
      return httpClient.get(url)
        .then((response) => {
          const records = response.data[0]
          commit('addRecords', records)
        })
        .finally(() => {
          commit('setNotLoading'),
          commit('setLoadComplete')
        })
    },
  },
}
