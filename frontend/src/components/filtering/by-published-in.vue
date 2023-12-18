<template lang="pug">
v-card(flat).flex-grow-1
  v-card-title Filter by journal
  v-card-subtitle Filter the reviewed preprints by the journal they were published in
  v-card-text
    v-autocomplete(
      v-model="selectedPublishers"
      :items="publishers.map(p => p.id)"
      :disabled="loadingRecords"
      label="Select publishers"
      multiple outlined deletable-chips compact
      chips).pa-0.mt-0
</template>

<script>

import { mapState } from 'vuex'

export default {
  data () {
    return {}
  },
  computed: {
    ...mapState('byFilters', ['publishers', 'loadingRecords', 'published_in']),

    selectedPublishers: {
      set(publishers) {
        this.$store.commit("byFilters/setPublishedIn", publishers);
      },
      get() {
        return this.published_in
      }
    }
  },
  methods: {},
}
</script>