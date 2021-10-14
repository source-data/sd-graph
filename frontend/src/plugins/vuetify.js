import Vue from 'vue'
import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'
import '@fortawesome/fontawesome-free/css/all.css' // Ensure you are using css-loader

Vue.use(Vuetify)

const opts = {
  icons: {
    iconfont: 'fa',
  },
}

export default new Vuetify(opts)