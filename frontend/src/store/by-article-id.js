import httpClient from '../lib/http'
import { BASE_URL } from '../lib/http'
import { parseDocmaps } from '@source-data/render-rev'

const docmapsApiPath = (doi) => `${BASE_URL}/api/v2/docmap/${doi}`

export const byArticleId = {
  namespaced: true,
  state: {
    reviewProcesses: {},
  },
  getters: {
    getReviewProcessForDoi: (state) => (doi) => {
      const data = state.reviewProcesses[doi]
      if (!data) {
        return undefined
      }
      const { reviewProcess } = data
      return reviewProcess
    }
  },
  mutations: {
    setReviewProcessForDoi(state, {doi, data}) {
      state.reviewProcesses[doi] = data
    },
  },
  actions: {
    async fetchReviewProcessForDoi({ commit, state }, doi) {
      if (state.reviewProcesses[doi]) {
        const { promise } = state.reviewProcesses[doi]
        return promise
      }
      // First we get the docmaps
      const url = docmapsApiPath(doi)
      const promise = httpClient.get(url)
        .then((response) => parseDocmaps(response.data))
        .then((reviewProcess) => {
          const data = { promise: Promise.resolve(), reviewProcess }
          commit('setReviewProcessForDoi', {doi, data})
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
        })
      const data = { promise, reviewProcess: undefined }
      commit('setReviewProcessForDoi', {doi, data})
      return promise
    },
  },
}
