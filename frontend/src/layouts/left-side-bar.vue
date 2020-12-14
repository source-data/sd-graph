<template lang="pug">
  v-navigation-drawer(app clipped permanent
        expand-on-hover)
    v-list(nav)
      router-link(to="/" active-class="is-active")
        v-list-item(index="0")
          v-icon(dense class="pa-1") mdi-home
          span Home
      router-link(to="/about")
        v-list-item(index="1")
          v-icon(dense class="pa-1") mdi-information-outline
          span About
      v-list-item(index="2" disabled)
        v-icon(dense class="pa-1") mdi-code-braces
        span For developers
      v-list-item(index="3" disabled)
        v-icon(dense class="pa-1") mdi-email-open-outline
        span Contact
    //- div(v-if="db_stats && !isCollapsed" style="padding:10px")
    v-divider
    v-list()
      v-list-item()
        v-icon(dense) mdi-database-outline
        //- small Database stats:
        small
          code {{ db_stats.preprints || 0 }}
          |  bioRxiv preprints loaded.
        //- p
        //-   code {{ db_stats.refereed_preprints || 0 }}
        //-   |  refereed preprints highlighted.
        //- p
        //-   code {{db_stats.autoannotated_preprints || 0 }}
        //-   |  COVID-19 preprints annotated automatically.




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