<template lang="pug">
  div
    h1 Quick Access
    el-tabs(type="border-card")
        el-tab-pane(label="By Method")
          .filter-list
            QuickAccessByMethod(@change="onChangeByMethod")
        el-tab-pane(label="By Molecule") Coming soon ...
        el-tab-pane(label="By observation and tested hypothesis")
            .filter-list
              QuickAccessByHyp(@change="onChangeByHyp")

</template>

<script>
import QuickAccessByMethod from './by-method.vue'
import QuickAccessByHyp from './by-hyp.vue'

export default {
  name: 'app',
  components: {
    QuickAccessByMethod,
    QuickAccessByHyp
  },
  methods: {
    onChangeByMethod (selectedItemId) {
      console.debug('onChangeByMethod',selectedItemId)
      //
      this.$store.commit('byMethod/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrentMethod')
    },
    onChangeByHyp (selectedItemId) {
      console.debug('onChangeByHyp',selectedItemId)
      //
      this.$store.commit('byHyp/showRecord', { id: selectedItemId })
      this.$store.dispatch('highlights/listByCurrentHyp')
    },
  },

}
</script>

<style scoped lang="scss">
.filter-list {
  max-height: 10em;
  padding-bottom: 1em;
  overflow: scroll;
}
</style>