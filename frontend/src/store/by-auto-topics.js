import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    operator: 'single',
    currentRecordIds: [],
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      return Object.values(state.records)  // so that component can iterate on an array instead of an object
    },
    currentRecord (state) {
      let result = {}
      if (state.operator == 'single') {
        let id = state.currentRecordIds[0]
        result = state.records[id]
      } else if (state.operator == 'and') {
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
        result = {papers: intersection}
      } else {
        let union = []
        let ids = [...state.currentRecordIds]
        ids.forEach(
          (id) => {
            union = [...union, ...state.records[id].papers]
          }
        )
        result = {papers: union}
      }
      return result
    },
    isLoaded (state) {
      return state.loadComplete
    }
  },
  mutations: {
    changeOperator (state, {operator}) {
        state.operator = operator
    },
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
      if (Array.isArray(ids)) {
        state.currentRecordIds = ids
      } else {
        state.currentRecordIds = [ids]
      }
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
