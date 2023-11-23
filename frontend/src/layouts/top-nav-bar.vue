<template lang="pug">
  v-app-bar(
    app
    height=100
    color="white"
  )
    v-row
      v-col(cols=3)
        Banner

      v-col(cols=9).pa-0.mt-2
        v-container.pa-0
          v-col.d-flex.flex-column
            a(href="https://embo.org" target="_blank" rel="noopener").pr-2.ml-auto
              img(src="../assets/EMBO_logo.svg" alt="EMBO Logo").logo-EMBO
            a(href="https://embopress.org" target="_blank" rel="noopener").pr-2.ml-auto
              img(src="../assets/EEB_EP_LOGO.png" alt="EMBO Press Logo").logo-EP
            a(href="https://sourcedata.io" target="_blank" rel="noopener").pr-2.ml-auto
              img(src="../assets/EEB_SD_LOGO.png" alt="SourceData Logo").logo-sd
    
    template(v-slot:extension)
      v-tabs(
        v-model="activeTab_"
        @change="onTabChange"
        center-active
        show-arrows
        wrap
        row
        justify-end
      )
          v-tab(to="/refereed-preprints") Browse reviewed preprints
          v-tab(to="/search" v-ripple="false" style="max-width:500px;").d-flex.flex-grow-1
            SearchBar(@submit="onSubmitSearch")
          v-spacer
          v-tab(to="/about") About
          v-tab(to="/for-developers") For developers
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

<style lang="scss" scoped>
.logo-EMBO {
  height: 29px;
  z-index: 1;
}

.logo-EP {
  height: 28px;
  z-index: 1;
}

.logo-sd {
  height: 12px;
  z-index: 1;
}
</style>