import httpClient from '../lib/http'

export default {
  namespaced: true,
  state: {
    records: {},
    loadingRecords: false,
    selectedTab: undefined,
    sortBy: 'posting_date',
    sortDirection: 'desc',
  },
  getters: {
    records (state) {
      return Object.values(state.records)
    },
    journalName (state, rootState, getters, rootGetters) {
      return rootGetters.journalName
    },
    selectedTab (state) {
      return state.selectedTab
    },
    getSortBy (state) {
      return state.sortBy
    },
    getSortDirection (state) {
      return state.sortDirection
    }
  },
  mutations: {
    updateSelectedTab (state, selectedTab) {
      state.selectedTab = selectedTab
    },
    /* *************************************************************************
    * RECORDS
    */
    resetRecords (state) {
       state.records = {}
    },
    setSortBy (state, { value }) {
      state.sortBy = value
    },
    setSortDirection (state, { value }) {
      state.sortDirection = value
    },
    sortRecords (state) {
      // sort records based on the property prop
      // default direction is ascending unless specified as 'desc'
      // computable sort metric defined by applying funct to the sorting property
      // note Date('2020-01-01') < Date('2020-01-02')
      const most_recent = (d1, d2) => {
        if (d1 > d2) {return d1}
        else {return d2}
      }
      const sortMethod = {
        pub_date: (r) => new Date(r.pub_date),
        posting_date: (r) => {
          return r.review_process.reviews
          .map(review => new Date(review.posting_date))
          .reduce(most_recent, new Date('2000-01-01'))
        }
      }
      const sort_metric = sortMethod[state.sortBy]
      const sign = state.sortDirection == 'desc' ? -1 : 1
      const sortedRecords = Object.values(state.records).slice().sort(
          (a, b) => sign * (sort_metric(a) - sort_metric(b))
        )
      const recordsById = {}
      sortedRecords.forEach((record) => {
          recordsById[record.id] = record
        })
      state.records = recordsById
    },
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
        if ('papers' in current) {
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
            commit('sortRecords')
            commit('setNotLoading')
          })
        } else {
          commit('setNotLoading')
          commit('addRecords', [])
          return {}
        }
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
