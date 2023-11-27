<template lang="pug">
  v-app-bar(
    app
    height=90
    color="tertiary"
    hide-on-scroll
  )
    v-row
      v-col(cols=3)
        Banner
    
    template(v-slot:extension)
      v-tabs(
        center-active
        show-arrows
        wrap
        row
        justify-end
      )
        v-tab(to="/refereed-preprints") Browse
        v-tab(to="/search" v-ripple="false" style="max-width:500px;").d-flex.flex-grow-1
          SearchBar
        v-spacer
        v-tab(to="/about") About
        v-tab(to="/contact") Contact
</template>

<script>

import Banner from './banner'
import SearchBar from '../components/filtering/by-simple-search-query.vue'

export default {
  components: {
    Banner,
    SearchBar
  }
}

</script>
