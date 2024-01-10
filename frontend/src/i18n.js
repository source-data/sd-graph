import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

export default new VueI18n({
  locale: 'en',
  messages: {
    en: {
      // the key format is "page.section.key", e.g. "home.title" will be used for the title of the home page
      // not found page
      'not_found.title': "Oops, you've encountered an error 404",
      'not_found.message': "It appears the page you were looking for doesn't exist. Sorry about that.",
    },
  }
})
