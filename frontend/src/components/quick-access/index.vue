<template lang="pug">
  div
    h1 Quick Access 
      el-button(v-if="loadingRecords" circle plain type="primary" :loading="true" size="mini" style="padding:2px") 
    el-tabs(@tab-click="onSelectTab" tab-position="top" v-model="activeTab")
      el-tab-pane(label="Refereed Preprints" name="byReviewingService")
        QuickAccessByReviewingService(@change="onChangeByReviewingService")
      //- el-tab-pane(label="By Method")
      //-   QuickAccessByMethod(@change="onChangeByMethod")
      el-tab-pane(label="COVID-19 hypotheses" name="byHyp")
        QuickAccessByHyp(@change="onChangeByHyp")
      //- el-tab-pane(label="By Molecule")
      //-   QuickAccessByMol(@change="onChangeByMol")
      el-tab-pane(label="Automagic selection" name="byAutomagic")
        QuickAccessByAutomagic
      el-tab-pane(name="fulltextSearch")
        span(slot="label") General search 
          i(class="el-icon-search")
        QuickAccessSearchBar(@submit="onSubmitSearch")
      el-divider
</template>

<script>
import QuickAccessByReviewingService from './by-reviewing-service.vue'
import QuickAccessByAutomagic from './by-automagic.vue'
import QuickAccessByMethod from './by-method.vue'
import QuickAccessByMol from './by-mol.vue'
import QuickAccessByHyp from './by-hyp.vue'
import QuickAccessSearchBar from './search-bar.vue'

import { mapState } from 'vuex'

export default {
  name: 'app',
  components: {
    QuickAccessByReviewingService,
    QuickAccessByAutomagic,
    QuickAccessByMethod,
    QuickAccessByMol,
    QuickAccessByHyp,
    QuickAccessSearchBar,
  },
  data () {
    return {
      activeTab: 'byReviewingService'
    }
  },
  methods: {
    onSelectTab () {
      this.$store.commit('highlights/updateSelectedTab', this.activeTab)
      this.$store.dispatch('highlights/listByCurrent', this.activeTab)
    },
    onSubmitSearch(term) {
      this.$store.dispatch('fulltextSearch/search', term).then(
        () => {this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')}
      )
    },
    onChangeByReviewingService (selectedItemId) {
      this.$store.commit('byReviewingService/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent', 'byReviewingService')
    },
    onChangeByHyp (selectedItemId) {
      this.$store.commit('byHyp/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent', "byHyp")
    },
  },
  computed: {
    ...mapState('highlights', ['loadingRecords'])
  }
}
</script>

<style lang="scss">
.spaced-row {
  padding: 1px;
}
</style>
