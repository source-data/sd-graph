import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    currentRecordIds: [],
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      return Object.values(state.records)  // so that component can iterate on an array instead of an object
    },
    currentRecord (state) {
      let intersection = []
      let ids = [...state.currentRecordIds]
      if (ids.length > 0) {
        intersection = [...state.records[ids[0]].papers]
        ids.shift()
        while (ids.length > 0) {
          const papers = state.records[ids[0]].papers
          const papers_doi = papers.map(p => p.doi)
          intersection = [...intersection].filter(x => papers_doi.includes(x.doi))
          ids.shift()
        }
      }
      const result = {papers: intersection}
      return result
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
        state.currentRecordIds = [firstRecord.id]
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
    showRecords (state, { ids }) {
      state.currentRecordIds = ids
    },
    closeRecordView (state) {
      state.currentRecordId = null
    },
  },
  actions: {
    getAll ({ commit }) {
      commit('setIsLoading')
      const url = '/api/v1/by_auto_topics/'
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
