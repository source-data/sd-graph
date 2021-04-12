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
      router-link(to="/for-developers")
        v-list-item(index="2")
          v-icon(dense class="pa-1") mdi-code-braces
          span For developers
      router-link(to="/contact")
        v-list-item(index="3")
          v-icon(dense class="pa-1") mdi-email-open-outline
          span Contact
    v-divider
    v-list()
      v-list-item()
        v-icon(dense) mdi-database-outline
        //- small Database stats:
        small
          code {{ db_stats.preprints || 0 }}
          |  bioRxiv preprints loaded (last update: 
          code {{lastUpdate}}
          | )


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
    lastUpdate() {
      const date = new Date(this.db_stats.last_updated)
      const yyyy = date.getFullYear()
      const mm = date.getMonth() + 1
      const dd = date.getDate()
      return `${yyyy}-${mm}-${dd}`
    },
  },
}
</script>

<style lang="scss" scoped>

</style>