<template lang="pug">
  div
    h1 Quick Access
    el-tabs(@tab-click="onSelectTab" tab-position="top")
      el-tab-pane(label="By Reviewing Service").filter-list
        QuickAccessByReviewingService(@change="onChangeByReviewingService")
      //- el-tab-pane(label="By Method").filter-list
      //-   QuickAccessByMethod(@change="onChangeByMethod")
      el-tab-pane(label="By tested hypothesis").filter-list
        QuickAccessByHyp(@change="onChangeByHyp")
      //- el-tab-pane(label="By Molecule").filter-list
      //-   QuickAccessByMol(@change="onChangeByMol")
      el-tab-pane(label="Automagic selection")
        QuickAccessByAutomagic
      el-divider

</template>

<script>
import QuickAccessByReviewingService from './by-reviewing-service.vue'
import QuickAccessByAutomagic from './by-automagic.vue'
import QuickAccessByMethod from './by-method.vue'
import QuickAccessByMol from './by-mol.vue'
import QuickAccessByHyp from './by-hyp.vue'


export default {
  name: 'app',
  components: {
    QuickAccessByReviewingService,
    QuickAccessByAutomagic,
    QuickAccessByMethod,
    QuickAccessByMol,
    QuickAccessByHyp,
  },
  methods: {
    onSelectTab (selectedTab) {
      if (selectedTab.label=="Automagic selection") {
        this.$store.dispatch('highlights/listByCurrent', 'byAutomagic')
      }
    },
    onChangeByReviewingService (selectedItemId) {
      this.$store.commit('byReviewingService/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent',  'byReviewingService')
    },
    onChangeByMethod (selectedItemId) {
      this.$store.commit('byMethod/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent',  'byMethod')
    },
    onChangeByMol (selectedItemId) {
      this.$store.commit('byMol/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent', 'byMol')
    },
    onChangeByHyp (selectedItemId) {
      this.$store.commit('byHyp/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrent', "byHyp")
    },
  },
}
</script>

<style lang="scss">
.spaced-row {
  padding: 1px;
}
</style>

<style scoped lang="scss">
.filter-list {
  // max-height: 10em;
  // overflow: scroll;
  // padding: 1em;
}
</style>
