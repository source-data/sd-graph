import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    currentRecordId: null,
    loadingRecords: false,
  },
  getters: {
    records (state) {
      return Object.values(state.records).slice().sort((a, b) => a.item_name.toLowerCase().localeCompare(b.item_name.toLowerCase()))
    },
    currentRecord (state) {
      return state.records[state.currentRecordId]
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
    /* *************************************************************************
    * NAVIGATION
    */
   setIsLoading (state) {
      state.loadingRecords = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
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
      const url = '/api/v1/by_method'
      return httpClient.get(url)
        .then((response) => {
          const records = response.data.map(preProcessRecord)
          commit('addRecords', records)
        })
        .finally(() => {
          commit('setNotLoading')
        })
    },
  },
}

function preProcessRecord (method) {
  return Object.assign({}, method, { id: method.item_ids[0] })
}