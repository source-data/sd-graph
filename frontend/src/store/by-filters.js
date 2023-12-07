import httpClient from '../lib/http'

const papersApiPath = '/api/v2/papers/'
const reviewersApiPath = '/api/v2/reviewing_services/'

const _serviceId2Slug = {
  'biorxiv': 'biorxiv',
  'medrxiv': 'medrxiv',
  'review commons': 'review-commons',
  'elife': 'elife',
  'embo press': 'embo-press',
  'peerage of science': 'peerage-of-science',
  'MIT Press - Journals': 'rrc19',
  'Peer Community In': 'peer-community-in',
  'peer ref': 'peer-ref',
}

const _serviceId2Name = {
  'biorxiv': 'bioRxiv', 
  'medrxiv': 'medRxiv',
  'review commons': 'Review Commons',
  'elife': 'eLife',
  'embo press': 'EMBO Press',
  'peerage of science': 'Peerage of Science',
  'MIT Press - Journals': 'Rapid Reviews: COVID-19',
  'Peer Community In': 'Peer Community In',
  'peer ref': 'Peer Ref'
}

const _allServiceIds = Object.keys(_serviceId2Slug)

export function serviceId2Slug(serviceId) {
  return _serviceId2Slug[serviceId]
}

export function serviceId2Name(serviceId) {
  return _serviceId2Name[serviceId]
}

export const byFilters = {
  namespaced: true,
  state: {
    reviewed_bys: _allServiceIds,
    query: "",

    records: {},
    paging: {
      page: 1,
      sortBy: 'preprint-date',
      sortOrder: 'desc'
    },
    reviewing_services: [],

    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    reviewingService (state) {
      return id => Object(state.reviewing_services.find(rs => rs.id === id))
    }
  },
  mutations: {
    /* *************************************************************************
    * Records and reviewing services
    */
    setRecords (state, data) {
      state.records = data.items
      state.paging = data.paging
    },

    setReviewingServices (state, reviewing_services) {
      state.reviewing_services = reviewing_services
    },
    /* *************************************************************************
    * Setters
    */
    setIsLoading (state) {
      state.loadingRecords = true
    },
    setLoadComplete (state) {
      state.loadComplete = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
    },
    setReviewedBys (state, reviewers) {
      state.reviewed_bys = reviewers
    },
    setCurrentPage (state, requestedPage) {
      state.paging.currentPage = requestedPage
    },
    setSortedBy (state, sortedBy) {
      state.paging.sortedBy = sortedBy
    },
    setSortedOrder (state, sortedOrder) {
      state.paging.sortedOrder = sortedOrder
    },
    setQuery (state, query) {
      state.query = query
    }
  },
  actions: {
    initialLoad ({ commit }) {
      commit('setIsLoading')

      // The initial load will fetch the first page, using all reviewers
      const params = new URLSearchParams();
      _allServiceIds.forEach(s => params.append("reviewedBy", s))

      // First we get the records
      return httpClient.get(papersApiPath, {params})
        .then((response) => {
          const data = response.data
          commit('setRecords', data)

          // And then we get the reviewing services
          httpClient.get(reviewersApiPath)
          .then((response) => {
            const data = response.data
            commit('setReviewingServices', data)
          })
          .finally(() => {
            commit('setNotLoading')
            commit('setLoadComplete')
          })
        })
    },

    updateRecords ({ commit, state }, resetPagination) {
      commit('setIsLoading')

      const params = new URLSearchParams();
      if (state.query !== "")
        params.append('query', state.query)
      state.reviewed_bys.forEach(s => params.append("reviewedBy", s))
      params.append('page', (resetPagination ? 1 : state.paging.currentPage))
      params.append('sortBy', state.paging.sortedBy)
      params.append('sortOrder', state.paging.sortedOrder)

      return httpClient.get(papersApiPath, {params: params})
        .then((response) => {
          const data = response.data
          commit('setRecords', data)
        })
        .finally(() => {
          commit('setNotLoading')
          commit('setLoadComplete')
        })
    },
  },
}
