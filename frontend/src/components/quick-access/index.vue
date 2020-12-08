<template lang="pug">
  v-card(class="pa-5")
    v-card-title Discover preprints with one of these methods
    v-tabs(v-model="activeTab_")
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
        QuickAccessByAutoTopics(@change="onChangeByAutoTopics")
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
import { REFEREED_PREPRINTSB, AUTO_TOPICS, AUTOMAGIC, FULLTEXT_SEARCH } from '../../components/quick-access/tab-names'
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
    onSubmitSearch(term) {
      this.$store.dispatch('fulltextSearch/search', term).then(
        () => {this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')}
      )
    },
    onChangeByAutoTopics (selectedItemIds) {
      this.$store.commit('byAutoTopics/showRecords', { ids: selectedItemIds })
      this.$store.dispatch('highlights/listByCurrent', "byAutoTopics")
    },
  },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    tabs () {
      return {REFEREED_PREPRINTSB, AUTO_TOPICS, AUTOMAGIC, FULLTEXT_SEARCH}
    }
  }
}
</script>

<style lang="scss">

</style>
