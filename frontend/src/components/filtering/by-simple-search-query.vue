<template lang="pug">
v-card(flat).flex-grow-1
  v-card-title Search for terms
  v-card-text.d-flex.d-flex-row.align-center
    v-text-field(
      v-model="currentQuery"
      :loading="loadingRecords"
      placeholder="keywords, authors, doi"
      prepend-icon="mdi-magnify"
      @keyup.enter="addQueryAndRefresh"
      hide-details
      outlined
      :disabled="disabled"
    ).mt-0.pt-0
    v-tooltip(bottom transition="fade-transition")
      template(v-slot:activator="{ on, hover, attrs }")
        v-btn(text v-bind="attrs" v-on="on" @click="clearQuery" icon :disabled="query === ''")
          v-icon(dense) mdi-close-circle
      span Clear search
    
</template>

<script>
import { mapState } from 'vuex'

export default {
  data: function() {
    return {
      disabled: false
    }
  },
  computed: {
    ...mapState('byFilters', ['query', 'loadingRecords']),

    currentQuery: {
      set(value) {
        this.$store.commit("byFilters/setQuery", value);
      },
      get() {
        return this.query
      }
    }
  },
  methods: {
    addQueryAndRefresh()  {
      this.$vuetify.goTo(0);
      this.disabled = true;
      this.$store.dispatch('byFilters/updateRecords');
    },
    clearQuery() {
      this.currentQuery = '';
      this.disabled = false;

      this.$vuetify.goTo(0);
      this.$store.commit("byFilters/setQuery", this.query);
      this.$store.dispatch('byFilters/updateRecords');
    },
  }
}
</script>