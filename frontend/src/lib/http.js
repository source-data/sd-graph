import axios from 'axios'

const BASE_URL = process.env.NODE_ENV == "production" ? 'https://covid19.sourcedata.io' : 'http://localhost:5000'
console.debug("process.env.NODE_ENV", process.env.NODE_ENV)

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
