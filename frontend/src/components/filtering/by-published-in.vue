<template lang="pug">
v-card(flat).flex-grow-1
  v-card-title Filter by journal
  v-card-subtitle Filter the reviewed preprints by the journal they were published in
  v-card-text
    v-autocomplete(
      v-model="selectedPublishers"
      :items="publishers"
      :item-value="publisherValue"
      :item-text="publisherText"
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
  methods: {
    publisherText(publisher) {
      return `(${publisher.n_papers}) ${publisher.id}`
    },
    publisherValue(publisher) {
      return publisher.id
    }
  },
}
</script>

<style lang="scss" scoped>
  ::v-deep .v-chip__content {
    display: inline !important;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 5px 20px 5px 0px;
  }

  ::v-deep .v-chip__content .v-chip__close {
    position: absolute;
    top: 6px;
    right: 10px;
  }
</style>