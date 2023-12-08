<template lang="pug">
v-app
  TopNavBar
  v-main.main-padding
    v-container.main-content
      router-view
  v-footer
    Footer
</template>

<script>
import TopNavBar from './layouts/top-nav-bar'
import Banner from './layouts/banner'
import Footer from './layouts/footer'

export default {
  name: 'App',

  components: {
    TopNavBar,
    Banner,
    Footer
  },
  metaInfo: {
    meta: [
      {
        vmid: 'description',
        name: 'description',
        content: 'Early Evidence Base (EEB) is an experimental platform that combines artificial intelligence with human curation and expert peer-review to highlight results posted in bioRxiv preprints developed by EMBO Press.',
      }
    ],
    title: 'Accessing early scientific findings',
    // all titles will be injected into this template
    titleTemplate: '%s | Early Evidence Base'
  },
  data: () => ({}),
  created() {
    this.$store.dispatch(`byFilters/initialLoad`);
  }
};
</script>


<style lang="scss">
html, body {
  padding:0;
  margin:0;
}

.v-application a {
  text-decoration: none;
}

.pointer {
  cursor: pointer;
}

// make the main container fluid up to a certain size
.container.main-content {
  max-width: 100%;
  width: 100%;
}

.v-input__control:has(input:disabled) {
  background-color:#dddddd !important;
}

.main-padding {
  padding-top: 150px;
}
</style>
