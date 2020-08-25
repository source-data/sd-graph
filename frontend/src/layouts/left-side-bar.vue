<template lang="pug">
  el-aside(width="180px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
    el-menu(default-active="1")
      router-link(to="/"  active-class="is-active")
        el-menu-item(index="0")
          span.el-icon-s-home
          | Home
      router-link(to="/about"  active-class="is-active")
        el-menu-item(index="1") About
      el-menu-item(index="2" disabled) For developers
      el-menu-item(index="3" disabled) Contact
    el-divider
    div(v-if="db_stats" style="padding:10px")
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
    ...mapGetters(['db_stats'])
  },
}
</script>
