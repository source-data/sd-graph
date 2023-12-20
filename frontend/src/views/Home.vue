<template lang="pug">
v-container(fluid).pa-0.ma-0
  v-btn(
    color="primary"
    fixed
    bottom
    right
    style="bottom: 75px;"
    fab @click="$vuetify.goTo(0)")
    v-icon mdi-arrow-up
  
  v-row.d-none.d-lg-flex.pa-3
    v-col(cols=3)
      v-card.fixed-filter-panel
        v-card-text
          v-row
            SearchBar
          v-row
            v-divider
          v-row
            ByReviewingService
          v-row
            v-divider
          v-row
            ByPublishedIn
    v-col(cols=9)
      v-row
        Highlights

  v-row(justify="center").d-lg-none
    v-dialog(
      v-model="showMobileFilterDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition")
      template(v-slot:activator="{ on, attrs }")
        v-btn(
          color="primary"
          v-bind="attrs"
          v-on="on").mr-auto.ml-3
          v-icon(left) mdi-filter-variant
          | Content filters
      v-card
        v-toolbar(color="tertiary")
          v-btn(icon @click="showMobileFilterDialog = false")
            v-icon mdi-close
          v-toolbar-title Content filters
          v-progress-circular(v-if="loadingRecords" :size="40" :width="7" color="primary" indeterminate).ml-auto
        v-card-text
          v-col.mt-3
            v-row
              SearchBar
            v-row
              v-divider
            v-row
              ByReviewingService
            v-row
              v-divider
            v-row
              ByPublishedIn
    Highlights
</template>


<script>
import { mapState } from 'vuex'
import Highlights from '../components/highlights/index.vue'
import ByReviewingService from '../components/filtering/by-reviewing-service.vue'
import ByPublishedIn from '../components/filtering/by-published-in.vue'
import SearchBar from '../components/filtering/by-simple-search-query.vue'

export default {
  name: 'home',
  components: {
    Highlights,
    ByReviewingService,
    ByPublishedIn,
    SearchBar
  },
  data() {
    return {
      showMobileFilterDialog: false
    }
  },
  computed: {
    ...mapState('byFilters', ['loadingRecords']),
  },
  props: {
    collection: String,
    service: String,
  },
  watch: {}
}
</script>

<style lang="scss">
.fixed-filter-panel {
  position: fixed !important;
  height: auto;
  width: calc(23.5%);
  top: 160px;
}

.v-app-bar--hide-shadow  ~ main .fixed-filter-panel {
  position: fixed !important;
  height: auto;
  width: calc(23.5%);
  top: 25px;
}
</style>

