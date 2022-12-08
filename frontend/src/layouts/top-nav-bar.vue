<template lang="pug">
    div
      v-app-bar(
        app 
        clipped-left 
        prominent
        height=220
        color="blue-grey darken-2"
        hide-on-scroll
        fade-img-on-scroll
        scroll-threshold="80"
        src="../assets/EEB_HP_Banner.svg"
      )
        Banner
        v-container(fluid).fill-height.align-end.pa-0
          v-row.align-center.pa-0
            .mr-auto
              a(href="https://embo.org" target="_blank" rel="noopener").pa-2
                img(src="../assets/EMBO_logo.svg" alt="EMBO Logo").logo-EMBO
            .d-flex
              a(href="https://embopress.org" target="_blank" rel="noopener").pa-2
                img(src="../assets/EEB_EP_LOGO.png" alt="EMBO Press Logo").logo-EP
              a(href="https://sourcedata.io" target="_blank" rel="noopener").pa-2
                img(src="../assets/EEB_SD_LOGO.png" alt="SourceData Logo")
</template>

<script>

import Banner from './banner'

export default {
  components: {
    Banner
  }
}
</script>

<style lang="scss" scoped>
.logo-EMBO {
  height: 55px;
}

.logo-EP {
  max-height: 80px;
}
</style>