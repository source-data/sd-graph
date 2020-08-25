import httpClient from '../lib/http'

const _serviceId2Slug = {
  'biorxiv': 'biorxiv',
  'medrxiv': 'medrxiv',
  'review commons': 'review_commons',
  'elife': 'elife',
  'embo press': 'embo_press',
  'peerage of science': 'peerage_of_science',
}

const _serviceSlug2Id = Object.keys(_serviceId2Slug).reduce((acc, serviceId) => {
  const serviceSlug = _serviceId2Slug[serviceId]
  return {...acc, [serviceSlug]: serviceId}
}, {})

const _serviceId2Name = {
  'biorxiv': 'bioRxiv',
  'medrxiv': 'medRxiv',
  'review commons': 'Review Commons',
  'elife': 'eLife',
  'embo press': 'EMBO Press',
  'peerage of science': 'Peerage of Science',
}

export function serviceId2Slug (serviceId) {
  return _serviceId2Slug[serviceId]
}
export function serviceSlug2Id (serviceSlug) {
  return _serviceSlug2Id[serviceSlug]
}

export function serviceId2Name (serviceId) {
  return _serviceId2Name[serviceId.toLowerCase()]
}

export const byReviewingService = {
  namespaced: true,
  state: {
    records: {},
    currentRecordId: 'review commons',
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      //return Object.values(state.records).slice().sort((a, b) => a.item_name.toLowerCase().localeCompare(b.item_name.toLowerCase()))
      return Object.values(state.records)
    },
    currentRecord (state) {
      return state.records[state.currentRecordId]
    },
    isLoaded (state) {
      return state.loadComplete
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
    setLoadComplete (state) {
      state.loadComplete = true
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
      const url = '/api/v1/by_reviewing_service/'
      return httpClient.get(url)
        .then((response) => {
          const records = response.data
          commit('addRecords', records)
        })
        .finally(() => {
          commit('setNotLoading'),
          commit('setLoadComplete')
        })
    },
  },
}
