<template lang="pug">
  div
    div(v-if="loadingRecords" )
      el-button(circle plain type="primary" :loading="true" size="mini" style="padding:2px")
    #quick-access-box(v-else="loadingRecords")
      el-tabs(@tab-click="onSelectTab" tab-position="top" v-model="activeTab")
        el-tab-pane(name="byReviewingService")
          span(slot="label")
            i(class="el-icon-reading")
            |  Refereed Preprints
          QuickAccessByReviewingService(@change="onChangeByReviewingService")
        //- el-tab-pane(label="By Method")
        //-   QuickAccessByMethod(@change="onChangeByMethod")
        el-tab-pane(name="byHyp")
          span(slot="label")
            i(class="fas el-icon-fa-flask")
            |  COVID-19 hypotheses
          QuickAccessByHyp(@change="onChangeByHyp")
        //- el-tab-pane(label="By Molecule")
        //-   QuickAccessByMol(@change="onChangeByMol")
        el-tab-pane(name="byAutomagic")
          span(slot="label")
            i(class="el-icon-magic-stick")
            |  Automagic COVID-19 selection
          QuickAccessByAutomagic
        el-tab-pane(name="fulltextSearch")
          span(slot="label")
            i(class="el-icon-search")
            |  Search COVID-19 preprints
          QuickAccessSearchBar(@submit="onSubmitSearch")
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
#quick-access-box {
  border: 1px solid #ddd;
  padding: 10px;
}
</style>
