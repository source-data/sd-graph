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
      multiple outlined deletable-chips
      chips)
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

<style lang="scss" scoped>
  ::v-deep .v-chip__content {
    display: inline-block !important;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: calc(100%);
    padding: 5px 20px 5px 0px;
  }

  ::v-deep .v-chip__content .v-chip__close {
    position: absolute;
    top: 6px;
    right: 0;
    margin-right: 5px;
    width: 24px;
  }
</style>