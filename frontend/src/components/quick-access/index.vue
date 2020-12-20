<template lang="pug">
  v-card(class="pa-5")
    v-card-title Discover preprints with one of these methods
    v-tabs(
      v-model="activeTab_"
      @change="onTabChange"
    )
      v-tab(to="/refereed-preprints")
        v-icon(class="px-1") mdi-book-open-variant
        | Refereed Preprints
      v-tab(to="/all/auto-topics")
        v-icon(class="px-1") mdi-help-circle-outline
        | Highlighted topics
      v-tab(to="/all/automagic")
        v-icon(class="px-1") mdi-auto-fix
        | Automagic selection
      v-tab(to="/all/search")
        v-icon(class="px-1") mdi-text-box-search-outline
        | Search preprints
      v-tab-item(value="/refereed-preprints")
        QuickAccessByReviewingService
      v-tab-item(value="/all/auto-topics")
        QuickAccessByAutoTopics(@change="onChangeByAutoTopics" @changeOperator="onChangeOperator")
      v-tab-item(value="/all/automagic")
        QuickAccessByAutomagic
      v-tab-item(value="/all/search")
        QuickAccessSearchBar(@submit="onSubmitSearch")
</template>

<script>
import QuickAccessByReviewingService from './by-reviewing-service.vue'
import QuickAccessByAutomagic from './by-automagic.vue'
import QuickAccessByAutoTopics from './by-auto-topics.vue'
import QuickAccessSearchBar from './search-bar.vue'
import { REFEREED_PREPRINTS, AUTO_TOPICS, AUTOMAGIC, FULLTEXT_SEARCH } from '../../components/quick-access/tab-names'
import { mapState } from 'vuex'

export default {
  name: 'QuickAccessIndex',
  components: {
    QuickAccessByReviewingService,
    QuickAccessByAutomagic,
    QuickAccessByAutoTopics,
    QuickAccessSearchBar,
  },
  data () {
    return {
      activeTab_: undefined,
    }
  },
  methods: {
    onTabChange(tabUrl) {
      let tabName = undefined
      let defaultSortBy = undefined
      switch (tabUrl) {
        case '/refereed-preprints':
          tabName = REFEREED_PREPRINTS
          defaultSortBy = 'posting_date'
          break
        case '/all/auto-topics':
          tabName = AUTO_TOPICS
          defaultSortBy = 'pub_date'
          break
        case '/all/automagic':
          tabName = AUTOMAGIC
          defaultSortBy = 'rank'
          break
        case '/all/search':
          tabName = FULLTEXT_SEARCH
          defaultSortBy = 'pub_date'
          break
      }
      this.$store.commit('highlights/updateSelectedTab', tabName)
      this.$store.commit('highlights/setSortBy', {value: defaultSortBy})
      this.$store.commit('highlights/setSortDirection', {value: 'desc'})
    },
    onSubmitSearch(term) {
      this.$store.dispatch('fulltextSearch/search', term).then(
        () => {this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')}
      )
    },
    onChangeByAutoTopics (selectedItemIds) {
      this.$store.commit('byAutoTopics/showRecords', { ids: selectedItemIds })
      this.$store.dispatch('highlights/listByCurrent', "byAutoTopics")
      this.$store.commit('highlights/updateCurrentPage', 1) // reset pagination if we are navigating to a different sub-app
    },
    onChangeOperator (value) {
      this.$store.commit('byAutoTopics/changeOperator', {'operator': value})
      this.$store.dispatch('highlights/listByCurrent', "byAutoTopics")
      this.$store.commit('highlights/updateCurrentPage', 1) // reset pagination if we are navigating to a different sub-app
    }
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
  }
}
</script>
