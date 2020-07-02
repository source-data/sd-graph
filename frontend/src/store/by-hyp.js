import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    currentRecordId: undefined,
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      return Object.values(state.records)
    },
    currentRecord (state) {
      return state.records[state.currentRecordId]
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
      const recordsById = {}
      records.forEach((record) => {
        recordsById[record.id] = record
      })
      state.records = recordsById
    },
    initCurrentRecord (state) {
        const firstRecord = Object.values(state.records)[0]
        state.currentRecordId = firstRecord.id
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
    showRecord (state, { id }) {
      state.currentRecordId = id
    },
    closeRecordView (state) {
      state.currentRecordId = null
    },
  },
  actions: {
    getAll ({ commit }) {
      commit('setIsLoading')
      const url = '/api/v1/by_hyp/'
      return httpClient.get(url)
        .then((response) => {
          const records = response.data
          commit('addRecords', records)
          commit('initCurrentRecord')
        })
        .finally(() => {
          commit('setNotLoading'),
          commit('setLoadComplete')
        })
    },
  },
}
