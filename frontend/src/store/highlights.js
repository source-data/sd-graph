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
    listByCurrent({ commit, rootGetters }, module) {
      commit('setIsLoading')
      const current = rootGetters[[module, 'currentRecord'].join('/')]
      const loadComplete = rootGetters[[module, 'isLoaded'].join('/')]
      if (loadComplete) {
        const dois = current.papers.map(c => c.doi)
        const promises = dois.map((doi) => {
          return httpClient.get(`/api/v1/doi/${doi}`)
        })
        return Promise.all(promises).then((responses) => {
          let non_empty = responses.filter(
            r => r.data.length > 0
          )
          const records = non_empty.reduce((acc, r) => {
            return [preProcessRecord(r.data[0], current), ...acc]
          }, [])
          commit('addRecords', records)
          return records
        }).finally(() => {
          commit('setNotLoading')
        })
      }
    },
  }
}

function preProcessRecord (record, current) {
  return Object.assign({}, record, {
    id: record.doi,
    info: current.papers.find(a => a.doi === record.doi).info
  })
}
