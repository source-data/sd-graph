<template lang="pug">
  div
    //- el-aside(max-width="180px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
    el-menu( :collapse="isCollapsed")
      router-link(to="/" active-class="is-active")
        el-menu-item(index="0")
          i.el-icon-s-home
          span(slot="title") Home
      router-link(to="/about" active-class="is-active")
        el-menu-item(index="1")
          i.el-icon-info
          span(slot="title") About
      el-menu-item(index="2" disabled)
        i.el-icon-lollipop
        span(slot="title") For developers
      el-menu-item(index="3" disabled)
        i.el-icon-s-promotion
        span(slot="title") Contact
    div(v-if="db_stats && !isCollapsed" style="padding:10px")
      el-divider
      small Database stats:
        p
          code {{ db_stats.biorxiv_preprints || 0 }}
          |  bioRxiv preprints loaded.
        p
          code {{ db_stats.refereed_preprints || 0 }}
          |  refereed preprints highlighted.
        p
          code {{db_stats.autoannotated_preprints || 0 }}
          |  COVID-19 preprints annotated automatically.




</template>


<script>
import { mapGetters } from 'vuex'

export default {
  name: 'LeftSideBar',
  computed: {
    ...mapGetters(['db_stats']),
    isCollapsed () {
      const mediaQuery = window.matchMedia( "(min-width: 812px)" );
      return !mediaQuery.matches
    },
  },
}
</script>

<style lang="scss" scoped>

</style>