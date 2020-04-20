import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    loadingRecords: false,
  },
  getters: {
    records (state) {
      return Object.values(state.records)
    },
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
    listByCurrentMethod ({ commit, rootGetters }) {
      commit('setIsLoading')
      const currentMethod = rootGetters['byMethod/currentRecord']
      const dois = currentMethod.content_ids.map(c => c.doi)
      const promises = dois.map((doi) => {
        return httpClient.get(`/api/v1/doi/${doi}`)
      })
      return Promise.all(promises).then((responses) => {
        const records = responses.reduce((acc, r) => {
          return [preProcessRecord(r.data[0], currentMethod), ...acc]
        }, [])

        commit('addRecords', records)
        return records
      }).finally(() => {
        commit('setNotLoading')
      })
    },
  },
}

function preProcessRecord (record, method) {
  return Object.assign({}, record, {
    id: record.doi,
    panel_ids: method.content_ids.find(a => a.doi === record.doi).panel_ids
  })
}
