import axios from 'axios'

const BASE_URL = process.env.NODE_ENV == "production" ? '' : 'http://localhost:5050'

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
