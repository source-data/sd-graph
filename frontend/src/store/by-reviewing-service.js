import httpClient from '../lib/http'

const _serviceId2Slug = {
  'biorxiv': 'biorxiv',
  'medrxiv': 'medrxiv',
  'review commons': 'review-commons',
  'elife': 'elife',
  'embo press': 'embo-press',
  'peerage of science': 'peerage-of-science',
  'MIT Press - Journals': 'rrc19',
  'Peer Community In': 'peer-community-in'

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
  } else if (/Peer Community In/.test(id)) {
    return 'Peer Community In'
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

export function getReviewingServiceDescription (serviceName) {
  switch (serviceName) {
    case 'review-commons':
      return '<p>Learn more about <i>Review Commons</i> at <a target="_blank" href="https://reviewcommons.org">https://reviewcommons.org</a></p>'
    case 'biorxiv':
      return '<p>Learn more about <i>bioRxiv</i> at <a target="_blank" href="https://www.biorxiv.org/">https://biorxiv.org/</a></p>'
    case 'medrxiv':
      return '<p>Learn more about <i>medRxiv</i> at <a target="_blank" href="https://www.medRxiv.org/">https://medRxiv.org/</a></p>'
    case 'elife':
      return '<p>Learn more about <i>eLife</i> Preprint Review at <a target="_blank" href="http://elifesci.org/preprint-review">http://elifesci.org/preprint-review</a></p>'
    case 'embo-press':
      return '<p>Learn more about <i>EMBO Press</i> Transparent Review at <a target="_blank" href="https://www.embopress.org/policies">https://embopress.org</a></p>'
    case 'peerage-of-science':
      return '<p>Learn more about <i>Peerage of Science</i> at <a target="_blank" href="https://www.peerageofscience.org/">https://peerageofscience.org/</a></p>'
    case 'rrc19':
      return '<p>Learn more about <i>Rapid Reviews: COVID-19</i> at <a target="_blank" href="https://rapidreviewscovid19.mitpress.mit.edu/">https://rapidreviewscovid19.mitpress.mit.edu/</a></p>'
    case 'peer-community-in':
      return '<p>Learn more about <i>Peer Community In</i> at <a target="_blank" href="https://peercommunityin.org/">https://peercommunityin.org/</a></p>'
    default: 
      break;
  }
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
