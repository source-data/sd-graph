<template lang="pug">
  div
    div(v-if="records.length > 0")
      h1 {{ records.length }} results found:
    p(v-else) No results
    v-container(:class="{'highlights-loading': loadingRecords}")
      v-row(v-for="article in records" :key="article.id")
        v-col
          HighlitedListItem(:article="article")
      br
</template>

<script>
import HighlitedListItem from './list-item.vue'
import { mapGetters, mapState } from 'vuex'


export default {
  components: {
    HighlitedListItem,
  },
  computed: {
    ...mapGetters('highlights', ['records']),
    ...mapState('highlights', ['loadingRecords'])
  },
}
</script>

<style lang="scss">
.highlights-loading {
  h1, h2, h3, h4, h5, h6, p, small, b, i, em, a, span, div {
    color: #bbb;
  }
}
</style>