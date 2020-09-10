<template lang="pug">
  div
    v-row(justify="center" v-if="loadingRecords")
      v-progress-circular(:size="70" :width="7" color="purple" indeterminate)
    div(v-else="loadingRecords")
    v-container(v-if="records.length > 0" :class="{'highlights-loading': loadingRecords}")
      h1 {{ records.length }} articles found:
    h1(v-if="records.length == 0 && !loadingRecords") No results
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
  h1, h2, h3, h4, h5, h6, p, small, b, i, em, a, span, div, .v-card .v-card__text .text--primary {
    color: #bbb !important;
  }
  .v-expansion-panel, .v-card {
    background-color: #eeeeee !important;
  }
}
</style>