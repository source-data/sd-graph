<template lang="pug">
v-app
  Snackbar
  TopNavBar
  v-main.main-padding
    v-container.main-content
      router-view
  v-footer
    Footer
</template>

<script>
import TopNavBar from './layouts/top-nav-bar'
import Snackbar from "./components/helpers/snackbar.vue";
import Footer from './layouts/footer'

export default {
  name: 'App',

  components: {
    TopNavBar,
    Footer,
    Snackbar
  },
  metaInfo () {
    return {
      meta: [
        {
          vmid: 'description',
          name: 'description',
          content: this.$t('meta.description'),
        }
      ],
      title: this.$t('meta.title'),
      // all titles will be injected into this template
      titleTemplate: (titleChunk) => titleChunk ?
        this.$t('meta.titleTemplate', {titleChunk})
        : this.$t('meta.title'),
    }
  },
  data: () => ({}),

  created() {
    this.$store.dispatch(`byFilters/initialLoad`, this.$route.query);
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

  @media only screen and (max-width: 1280px) {
    padding: 10px !important;
  }
}

.v-input__control:has(input:disabled) {
  background-color:#dddddd !important;
}

.main-padding {
  padding-top: 150px;
}
</style>
