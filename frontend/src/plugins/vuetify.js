import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import '@fortawesome/fontawesome-free/css/all.css' // Ensure you are using css-loader

Vue.use(Vuetify)

const opts = {
  icons: {
    iconfont: 'fa',
  },
  theme: {
    themes: {
      light: {
        primary: '#0a5769',
        secondary: '#217b90',
        tertiary: '#EFF5FA',
        accent: '#8c9eff',
        error: '#b71c1c',
      },
    },
  },
}

export default new Vuetify(opts)