import httpClient from '../lib/http'
import { REFEREED_PREPRINTS, AUTO_TOPICS, AUTOMAGIC, FULLTEXT_SEARCH } from '../components/quick-access/tab-names'

export default {
  namespaced: true,
  state: {
    records: {},
    loadingRecords: false,
    selectedTab: undefined,
    sortBy: 'posting_date',
    sortDirection: 'desc',
    page: {
      [AUTO_TOPICS]: 1,
      [REFEREED_PREPRINTS]: 1,
      [AUTOMAGIC]: 1,
      [FULLTEXT_SEARCH]: 1
    }
  },
  getters: {
    records (state) {
      return Object.values(state.records)
    },
    selectedTab (state) {
      return state.selectedTab
    },
    getSortBy (state) {
      return state.sortBy
    },
    getSortDirection (state) {
      return state.sortDirection
    },
    currentPage(state) {
      return state.page[state.selectedTab]
    }
  },
  mutations: {
    updateSelectedTab (state, selectedTab) {
      state.selectedTab = selectedTab
    },
    updateCurrentPage (state, page) {
      const tab = state.selectedTab
      // using spreading instead of direct assignment to trigger reactivity
      // see https://vuex.vuejs.org/guide/mutations.html#mutations-follow-vue-s-reactivity-rules
      state.page = {...state.page, [tab]: page}
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
        },
        rank: (r) => {
          return parseInt(r.rank)
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
      if (!loadComplete || !('papers' in current)) {
        commit('setNotLoading')
        commit('addRecords', [])
        return
      }
      httpClient.post('/api/v1/dois/', {
          dois: current.papers.map(c => c.doi),
        })
        .then((response) => {
          const records = response.data.reduce((acc, article) => {
            return [preProcessRecord(article, current), ...acc]
          }, [])
          commit('addRecords', records)
        })
        .finally(() => {
          commit('sortRecords')
          commit('setNotLoading')
        })
    },
  }
}

function preProcessRecord (record, current) {
  return Object.assign({}, record, {
    id: record.doi,
    // eliminate this; info specific to sub application is copied to papers to display
    // should be provided by /api/v1/doi and offer universal sorting methods.
    rank: current.papers.find(a => a.doi === record.doi).rank
  })
}
