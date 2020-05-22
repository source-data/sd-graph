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
    listByCurrentMethod({ commit, rootGetters }) {
      commit('setIsLoading')
      const current = rootGetters['byMethod/currentRecord']
      const dois = current.papers.map(c => c.doi)
      const promises = dois.map((doi) => {
        return httpClient.get(`/api/v1/doi/${doi}`)
      })
      return Promise.all(promises).then((responses) => {
        const records = responses.reduce((acc, r) => {
          return [preProcessRecord(r.data[0], current), ...acc]
        }, [])

        commit('addRecords', records)
        return records
      }).finally(() => {
        commit('setNotLoading')
      })
    },
    listByCurrentHyp({ commit, rootGetters }) {
        commit('setIsLoading')
        const current = rootGetters['byHyp/currentRecord'] //how can I specify the module via a variable when calling action?
        const dois = current.papers.map(c => c.doi)
        const promises = dois.map((doi) => {
          return httpClient.get(`/api/v1/doi/${doi}`)
        })
        return Promise.all(promises).then((responses) => {
          const records = responses.reduce((acc, r) => {
            return [preProcessRecord(r.data[0], current), ...acc]
          }, [])
  
          commit('addRecords', records)
          return records
        }).finally(() => {
          commit('setNotLoading')
        })
      },
  }
}

function preProcessRecord (record, current) {
  return Object.assign({}, record, {
    id: record.doi,
    //panel_ids: method.content_ids.find(a => a.doi === record.doi).panels.map(p => p.id),
    panels: current.papers.find(a => a.doi === record.doi).panels
  })
}
