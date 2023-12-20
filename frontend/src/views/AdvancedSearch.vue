<template lang="pug">
v-container(fluid).pa-0.ma-0
  v-row.d-none.d-lg-flex.pa-3
    v-col.col-lg-8.col-md-9.col-sm-10.col-xs-12.ml-auto.mr-auto
      v-card
        v-card-text
          AdvancedSearchForm
    v-row(cols=9)
      v-col
        Highlights

  v-row(justify="center").d-lg-none
    v-dialog(
      v-model="showMobileAdvancedSearchDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition")
      template(v-slot:activator="{ on, attrs }")
        v-btn(
          color="primary"
          v-bind="attrs"
          v-on="on").mr-auto.ml-3
          v-icon(left) mdi-filter-variant
          | Show advanced search form
      v-card(flat)
        v-toolbar(color="tertiary")
          v-btn(icon @click="showMobileAdvancedSearchDialog = false")
            v-icon mdi-close
          v-toolbar-title Content filters
        v-card-text
          AdvancedSearchForm.mt-3
    Highlights
</template>


<script>
import { mapState } from 'vuex'
import Highlights from '../components/highlights/index.vue'
import AdvancedSearchForm from '../components/advanced-search/advanced-search-form.vue'

export default {
  name: 'home',
  components: {
    Highlights,
    AdvancedSearchForm
  },
  data() {
    return {
      showMobileAdvancedSearchDialog: false
    }
  },
  computed: {
    ...mapState('byFilters', ['loadingRecords']),
  },
  props: {
    collection: String,
    service: String,
  },
}
</script>

