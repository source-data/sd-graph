<template lang="pug">
  v-card(flat).col-lg-8.col-md-9.col-sm-10.col-xs-12.ml-auto.mr-auto
    span.d-flex.flex-row.align-center.mt-3
      a(href="https://embo.org" target="_blank" rel="noopener").pr-2.ml-auto
        img(src="../assets/EMBO_logo.svg" :alt="$t('logo.alt.embo')").logo-EMBO
      a(href="https://embopress.org" target="_blank" rel="noopener").pr-2
        img(src="../assets/EEB_EP_LOGO.png" :alt="$t('logo.alt.embo_press')").logo-EP
      a(href="https://sourcedata.io" target="_blank" rel="noopener").pb-1.mr-auto
        img(src="../assets/EEB_SD_LOGO.png" :alt="$t('logo.alt.sourcedata')").logo-SD

    v-card-title {{ $t('about.title') }}
    v-card-text.text-body-1(v-html="$t('about.text_html')")
</template>

<style lang="scss" scoped>
.logo-EP {
  height: 30px;
}

.logo-EMBO {
  height: 30px;
}

.logo-SD {
  height: 15px;
}

@media only screen and (max-width: 600px) {
  .logo-EP {
    height: 22px;
  }
  .logo-EMBO {
    height: 22px;
  }
  .logo-SD {
    height: 13px;
  }
}

</style>