<template lang="pug">
  v-app-bar(
    app
    height=90
    color="tertiary"
    hide-on-scroll
    scroll-threshold=0
    scroll-off-screen tile elevation=1
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
        v-spacer
        v-tab(to="/about") About
        v-tab(to="/contact") Contact
</template>

<script>

import Banner from './banner'

export default {
  components: {
    Banner
  }
}

</script>
