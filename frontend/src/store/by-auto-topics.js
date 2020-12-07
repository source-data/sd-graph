import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    // entity_highlighted_names: Array(16)
    // 0: doi: "10.1101/2020.08.12.247460"
    // pub_date: "2020-08-12T00:00:00Z"
    // rank: ""
    // id: 1
    // papers: (...)
    // topics: Array(7)
    // topics_name: "tumor, breast, endothelial, lung, kinase, oncogenic, phosphorylation"
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
      console.debug('ids', ids)
      if (ids.length > 0) {
        intersection = [...state.records[ids[0]].papers]
        ids.shift()
        while (ids.length > 0) {
          const papers = state.records[ids[0]].papers
          intersection = [...intersection].filter(x => papers.includes(x))
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
