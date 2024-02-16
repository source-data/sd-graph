<template lang="pug">
  v-card(flat).col-lg-8.col-md-9.col-sm-10.col-xs-12.ml-auto.mr-auto
    v-card-title {{ $t('about.heading') }}
    v-card-text.text-body-1(v-html="$t('about.text_html')")
</template>

<script>
export default {
  metaInfo () {
    return {
      title: this.$t('about.title'),
    }
  },
};
</script>

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