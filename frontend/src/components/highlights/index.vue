<template lang="pug">
  div
    div(v-if="loadingRecords")
      p(style="text-align: center")
        el-button(type="primary" :loading="true" round plain)
    div(v-else="loadingRecords")
      HighlitedListItem(:article="article" v-for="article in records")
</template>

<script>
import HighlitedListItem from './list-item.vue'
import { mapState, mapGetters } from 'vuex'

export default {
  components: {
    HighlitedListItem,
  },
  // methods: {
  //   displayJournal(key) {
  //     const low_key = key.toLowerCase()
  //     const journal_labels = {
  //       biorxiv: 'bioRxiv', 
  //       medrxiv: 'medRxiv',
  //       'review commons': 'Review Commons',
  //       elife: 'eLife',
  //       'embo press': 'EMBO Press',
  //     }
  //     return journal_labels[low_key]
  //   },
  // },
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    ...mapGetters('highlights', ['records']),
  },
}
</script>