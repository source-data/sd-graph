<template lang="pug">
  div
    el-tabs(tab-position="top" v-model="activeTab_")
      el-tab-pane(:name="tabs.REFEREED_PREPRINTS_TAB")
        router-link(to="/refereed_preprints/review_commons" slot="label") Refereed Preprints
        QuickAccessByReviewingService
      el-tab-pane(:name="tabs.COVID19_HYP_TAB")
        router-link(to="/covid19/by_hyp" slot="label") COVID-19 hypotheses
        QuickAccessByHyp(@change="onChangeByHyp")
      el-tab-pane(:name="tabs.COVID19_AUTOMAGIC_TAB")
        router-link(to="/covid19/automagic" slot="label") Automagic COVID-19 selection
        QuickAccessByAutomagic
      el-tab-pane(:name="tabs.COVID19_SEARCH")
        router-link(to="/covid19/search" slot="label") Search preprints
        QuickAccessSearchBar(@submit="onSubmitSearch")
</template>

<script>
import QuickAccessByReviewingService from './by-reviewing-service.vue'
import QuickAccessByAutomagic from './by-automagic.vue'
import QuickAccessByMethod from './by-method.vue'
import QuickAccessByMol from './by-mol.vue'
import QuickAccessByHyp from './by-hyp.vue'
import QuickAccessSearchBar from './search-bar.vue'
import { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, COVID19_SEARCH } from '../../components/quick-access/tab-names'
import { mapState } from 'vuex'

export default {
  name: 'QuickAccessIndex',
  components: {
    QuickAccessByReviewingService,
    QuickAccessByAutomagic,
    QuickAccessByMethod,
    QuickAccessByMol,
    QuickAccessByHyp,
    QuickAccessSearchBar,
  },

  props: {
    activeTab: String,
  },
  data () {
    return {
      activeTab_: undefined,
    }
  },
  mounted () {
    this.activeTab_ = this.activeTab
  },
  watch: {
    activeTab (val) {
      // element's `el-tabs` component wants to have v-model assigned to it, so we will have to give
      // to him and keep it in sync with whatevr our parent component passes down as prop.
      // This little trick allows the parent component to dictate which tab is now active
      // which in turn is determined by the current route
      if (this.activeTab_ !== val) {
        this.activeTab_ = val
      }
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
      return { REFEREED_PREPRINTS_TAB, COVID19_HYP_TAB, COVID19_AUTOMAGIC_TAB, COVID19_SEARCH }
    }
  }
}
</script>

<style lang="scss">

</style>
