<template lang="pug">
v-card(flat).flex-grow-1
  v-card-title {{ $t('filters.search.title') }}
  v-card-subtitle {{ $t('filters.search.subtitle') }}
  v-card-text.d-flex.d-flex-row.align-center
    v-text-field(
      :value="currentQuery" v-on:keyup.enter="currentQuery = $event.target.value"
      :placeholder="$t('filters.search.placeholder')"
      prepend-icon="mdi-magnify"
      hide-details
      outlined
    ).mt-0.pt-0
    v-tooltip(color="tooltip" bottom transition="fade-transition")
      template(v-slot:activator="{ on, hover, attrs }")
        v-btn(text v-bind="attrs" v-on="on" @click="currentQuery = ''" icon :disabled="query === ''")
          v-icon(dense) mdi-close-circle
      span {{ $t('filters.search.clear') }}
</template>

<script>
import { mapState } from 'vuex'

export default {
  data: function() {
    return {
    }
  },
  computed: {
    ...mapState('byFilters', ['query', 'loadingRecords']),

    currentQuery: {
      set(value) {
        this.$vuetify.goTo(0);
        this.$store.commit("byFilters/setQuery", value);
      },
      get() {
        return this.query
      }
    }
  },
  methods: {}
}
</script>