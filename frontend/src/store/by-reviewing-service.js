import httpClient from '../lib/http'

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

const _serviceSlug2Id = Object.keys(_serviceId2Slug).reduce((acc, serviceId) => {
  const serviceSlug = _serviceId2Slug[serviceId]
  return {...acc, [serviceSlug]: serviceId}
}, {})


function _serviceId2Name (id) {
  if (id === 'biorxiv') {
    return 'bioRxiv' 
  } else if (id === 'medrxiv') {
    return 'medRxiv'
  } else if (id === 'review commons') {
    return 'Review Commons'
  } else if (id === 'elife') {
    return 'eLife'
  } else if (id === 'embo press') {
    return 'EMBO Press'
  } else if (id === 'peerage of science') {
    return 'Peerage of Science' 
  } else if (id === 'MIT Press - Journals') {
    return 'Rapid Reviews: COVID-19'
  } else if (/peer community in/i.test(id)) {
    return 'Peer Community In'
  } else if (id == 'peer ref') {
    return 'Peer Ref'
  }
}

export function serviceId2Slug (serviceId) {
  return _serviceId2Slug[serviceId]
}
export function serviceSlug2Id (serviceSlug) {
  return _serviceSlug2Id[serviceSlug]
}

export function serviceId2Name (serviceId) {
  return _serviceId2Name(serviceId)
}

export function serviceSlug2name(serviceSlug) {
  return _serviceId2Name(_serviceSlug2Id[serviceSlug])
}


export const byReviewingService = {
  namespaced: true,
  state: {
    records: {},
    reviewing_service_descriptions: {},
    currentRecordId: 'review commons',
    loadingRecords: false,
    loadComplete: false,
  },
  getters: {
    records (state) {
      //return Object.values(state.records).slice().sort((a, b) => a.item_name.toLowerCase().localeCompare(b.item_name.toLowerCase()))
      return Object.values(state.records)
    },
    reviewingService (state) {
      return id => Object(state.reviewing_service_descriptions[id])
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
      const reviewing_service_descriptions = {}
      records.forEach((record) => {
        recordsById[record.id] = record
        reviewing_service_descriptions[record.id] = record.reviewing_service_description
      })
      state.records = recordsById
      state.reviewing_service_descriptions = reviewing_service_descriptions
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
