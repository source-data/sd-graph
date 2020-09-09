<template lang="pug">
  v-card(class="pa-5")
    v-card-title Discover preprints with one of these methods
    v-tabs(v-model="activeTab_")
      v-tab(to="/refereed-preprints")
        v-icon(class="px-1") mdi-book-open-variant
        | Refereed Preprints
      v-tab(to="/covid19/by-hyp")
        v-icon(class="px-1") mdi-help-circle-outline
        | COVID-19 hypotheses
      v-tab(to="/covid19/automagic")
        v-icon(class="px-1") mdi-auto-fix
        | Automagic COVID-19 selection
      v-tab(to="/all/search")
        v-icon(class="px-1") mdi-text-box-search-outline
        | Search preprints
      v-tab-item(value="/refereed-preprints")
        QuickAccessByReviewingService
      v-tab-item(value="/covid19/by-hyp")
        QuickAccessByHyp(@change="onChangeByHyp")
      v-tab-item(value="/covid19/automagic")
        QuickAccessByAutomagic
      v-tab-item(value="/all/search")
        QuickAccessSearchBar(@submit="onSubmitSearch")
</template>

<script>
import QuickAccessByReviewingService from './by-reviewing-service.vue'
import QuickAccessByAutomagic from './by-automagic.vue'
// import QuickAccessByMethod from './by-method.vue'
// import QuickAccessByMol from './by-mol.vue'
import QuickAccessByHyp from './by-hyp.vue'
import QuickAccessSearchBar from './search-bar.vue'
import { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, FULLTEXT_SEARCH } from '../../components/quick-access/tab-names'
import { mapState } from 'vuex'

export default {
  name: 'QuickAccessIndex',
  components: {
    QuickAccessByReviewingService,
    QuickAccessByAutomagic,
    // QuickAccessByMethod,
    // QuickAccessByMol,
    QuickAccessByHyp,
    QuickAccessSearchBar,
  },
  data () {
    return {
      activeTab_: undefined,
    }
  },
  methods: {
    onSubmitSearch(term) {
      this.$store.dispatch('fulltextSearch/search', term).then(
        () => {this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')}
      )
    },
    onChangeByHyp (selectedItemId) {
      this.$store.commit('byHyp/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent', "byHyp")
    },
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    tabs () {
      return { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, FULLTEXT_SEARCH }
    }
  }
}
</script>

<style lang="scss">

</style>
