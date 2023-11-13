import axios from 'axios'

function baseUrl(node_env) {
  switch (node_env) {
    case 'production':
      return ''
    case 'serverless':
      return 'https://eeb-dev.embo.org'
    default:
      return 'http://localhost:5050'
  }
}
export const BASE_URL = baseUrl(process.env.NODE_ENV)

const httpClient = axios.create({
  baseURL: BASE_URL,
})

export default httpClient

export const httpMock = {
  get (url, responseData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ data: responseData })
      }, 700)
    })
  },
  patch (url, payload) {
    return new Promise((resolve) => {
      setTimeout(() => {
        // resolve(candidatesDummyData)
        resolve({ data: payload })
      }, 300)
    })
  },
}
