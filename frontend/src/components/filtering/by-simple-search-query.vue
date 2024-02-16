<template lang="pug">
v-card(flat).flex-grow-1
  v-card-title {{ $t('filters.search.title') }}
  v-card-subtitle {{ $t('filters.search.subtitle') }}
  v-card-text.d-flex.d-flex-row.align-center
    v-text-field(
      v-model="inputQuery"
      v-on:keyup.enter="setActiveQuery"
      @click:append-outer="setActiveQuery"
      @click:clear="clearActiveQuery"
      :placeholder="$t('filters.search.placeholder')"
      append-outer-icon="mdi-magnify"
      outlined
      clearable
      :error-messages="errorMessages"
    ).mt-0.pt-0
</template>

<script>
import { mapState } from 'vuex'

export default {
  data: function() {
    return {
      inputQuery: null,
      minQueryLength: 3,
      errorMessages: [],
    }
  },
  computed: {
    ...mapState('byFilters', ['query', 'loadingRecords']),

    activeQuery: {
      set(value) {
        this.$vuetify.goTo(0);
        this.$store.commit("byFilters/setQuery", value);
      },
      get() {
        return this.query
      }
    }
  },
  methods: {
    clearActiveQuery() {
      this.errorMessages = [];
      if (this.activeQuery) {
        this.activeQuery = '';
      }
    },
    setActiveQuery() {
      this.errorMessages = [];
      const inputQuery = this.inputQuery || '';
      if (inputQuery.length < this.minQueryLength) {
        this.errorMessages = [this.$t('filters.search.errorMessages.minLength', { min: this.minQueryLength })];
        return;
      }
      if (inputQuery === this.activeQuery) {
        return;
      }
      this.activeQuery = inputQuery;
    }
  }
}
</script>