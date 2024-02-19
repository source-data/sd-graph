import httpClient from '../lib/http'
import router from '@/router'

const papersApiPath = '/api/v2/papers/'
const reviewersApiPath = '/api/v2/reviewing_services/'
const publishersApiPath = '/api/v2/publishers/'

const _serviceId2Name = {
  'biorxiv': 'bioRxiv', 
  'medrxiv': 'medRxiv',
  'review commons': 'Review Commons',
  'elife': 'eLife',
  'embo press': 'EMBO Press',
  'peerage of science': 'Peerage of Science',
  'mit press - journals': 'Rapid Reviews: COVID-19',
  'peer community in': 'Peer Community In',
  'peer ref': 'Peer Ref'
}

export function normalizeServiceName(serviceName) {
  return serviceName.toLowerCase().replaceAll(/[\W_]+/g, "");
}

export function serviceId2Name(serviceId) {
  return serviceId ? _serviceId2Name[serviceId.toLowerCase()] : serviceId
}

export const byFilters = {
  namespaced: true,
  state: {
    reviewed_bys: [],
    published_in: [],
    query: "",

    records: {},
    paging: {},
    reviewing_services: [],
    publishers: [],

    error: null,
    loadingRecords: false,
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

    setPublishers (state, publishers) {
      state.publishers = publishers
    },
    /* *************************************************************************
    * Setters
    */
    setIsLoading (state) {
      state.loadingRecords = true
    },
    setNotLoading (state) {
      state.loadingRecords = false
    },
    setReviewedBys (state, reviewers) {
      state.reviewed_bys = reviewers
    },
    setPublishedIn (state, publishedIn) {
      state.published_in = publishedIn;
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
    },
    maybeSetInitialValuesFromUrlParams(state, urlParams) {
      if (urlParams.page)
        state.paging.currentPage = urlParams.page
      if (urlParams.reviewedBy)
        state.reviewed_bys = [urlParams.reviewedBy].flat() // one liner to deal with having one or multiple reviewedBy params
      if (urlParams.publishedIn)
        state.published_in = [urlParams.publishedIn].flat() // one liner to deal with having one or multiple reviewedBy params
        if (urlParams.sortBy)
        state.paging.sortedBy = urlParams.sortBy
      if (urlParams.sortOrder)
        state.paging.sortedOrder = urlParams.sortOrder
      if (urlParams.query)
        state.query = urlParams.query
    }
  },
  actions: {
    initialLoad ({ commit, state }, urlParams) {
      commit('setIsLoading')
      commit('maybeSetInitialValuesFromUrlParams', urlParams)

      const routeParams = {
        // Conditionally create the request params given the initial state - if no params were passed
        // in the URL, nothing will be passed
        ...(state.query !== "" ? {query: state.query} : {}),
        ...(state.reviewed_bys.length !== 0 ? {reviewedBy: state.reviewed_bys} : {}),
        ...(state.published_in.length !== 0 ? {publishedIn: state.published_in} : {}),
        ...(state.paging.currentPage ? { page: state.paging.currentPage} : {}),
        ...(state.paging.sortedBy ? {sortBy: state.paging.sortedBy} : {}),
        ...(state.paging.sortedOrder ? {sortOrder: state.paging.sortedOrder} : {}),
      }

      // First we get the records
      return httpClient.get(papersApiPath, { params: new URLSearchParams(routeParams) })
        .then((response) => {
          const data = response.data
          commit('setRecords', data)

          // Then we get the reviewing services
          httpClient.get(reviewersApiPath)
          .then((response) => {
            const data = response.data
            commit('setReviewingServices', data)

            // And then we get the publisher data
            httpClient.get(publishersApiPath)
              .then((response) => {
                const data = response.data
                commit('setPublishers', data)
              })
              .catch(function () {
                state.error = "snack.message.error.server"
              })
              .finally(() => {
                commit('setNotLoading')
              })
          })
          .catch(function () {
            commit("setSnack", 
              { message: "snack.message.error.server", 
                color: "red" }, 
              { root: true });  
          })
          .finally(() => {
            commit('setNotLoading')
          })
        })
        .catch(function (error) {
          if (error.response.status === 400) {
            commit("setSnack", 
              { message: "snack.message.error.request", 
                color: "red" }, 
              { root: true });
          } else {
            commit("setSnack", 
              { message: "snack.message.error.server", 
                color: "red" }, 
              { root: true });
          } 

          commit('setNotLoading')
        })
    },

    updateRecords ({ commit, state }, resetPagination) {
      commit('setIsLoading')

      const routeParams = {
        ...(state.query !== "" ? {query: state.query} : {}),
        ...(state.reviewed_bys.length !== 0 ? {reviewedBy: state.reviewed_bys} : {}),
        ...(state.published_in.length !== 0 ? {publishedIn: state.published_in} : {}),
        page: (resetPagination ? 1 : state.paging.currentPage),
        sortBy: state.paging.sortedBy,
        sortOrder: state.paging.sortedOrder
      }

      // Before we issue the request set query params in the URL
      router.push({ query: routeParams });
      return httpClient.get(papersApiPath, { params: new URLSearchParams(routeParams) })
        .then((response) => {
          const data = response.data
          commit('setRecords', data)
        })
        .catch(function () {
          commit("setSnack", 
            { message: "snack.message.error.server", 
              color: "red" }, 
            { root: true });
        })
        .finally(() => {
          commit('setNotLoading')
        })
    },
  },
}
