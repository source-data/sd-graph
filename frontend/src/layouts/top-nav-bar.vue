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
        div(style="height: 100%; width: 100%").d-flex.align-end
          div(style="width: 100%").d-flex.align-center
            div.mr-auto
              a(href="https://embo.org" target="_blank" rel="noopener")
                img(src="../assets/EEB_E_LOGO.png" alt="EMBO Logo").logo-EMBO
            .d-flex
              a(href="https://embopress.org").pa-2
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
  max-height: 60px;
}

.logo-EP {
  max-height: 80px;
}

</style>