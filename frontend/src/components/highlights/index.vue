<template lang="pug">
  div
    h1 Highlights
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
  computed: {
    ...mapState('highlights', ['loadingRecords']),
    ...mapGetters('highlights', ['records']),
  },
}
</script>