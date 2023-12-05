<template lang="pug">
v-container(fluid).pa-0.ma-0
  v-row.pa-3
    v-col(cols=3)
      v-card.fixed-filter-panel
        v-card-text
          v-row
            SearchBar
          v-row
            v-divider
          v-row
            ByReviewingService
    v-col(cols=9)
      v-row
        Highlights
</template>


<script>
import Highlights from '../components/highlights/index.vue'
import ByReviewingService from '../components/filtering/by-reviewing-service.vue'
import SearchBar from '../components/filtering/by-simple-search-query.vue'

export default {
  name: 'home',
  components: {
    Highlights,
    ByReviewingService,
    SearchBar
  },
  props: {
    collection: String,
    service: String,
  },

  created () {
    this.$store.dispatch(`byFilters/initialLoad`);
    return true;
  },

}
</script>

<style lang="scss">
.fixed-filter-panel {
  position: sticky !important;
  top: 160px;
}

.v-app-bar--hide-shadow  ~ main .fixed-filter-panel {
  position: sticky !important;
  top: 25px;
}
</style>

