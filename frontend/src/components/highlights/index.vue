<template lang="pug">
  div
    v-row(justify="center" v-if="loadingRecords")
      v-progress-circular(:size="70" :width="7" color="purple" indeterminate)
    div(v-else="loadingRecords")
    v-container(v-if="records.length > 0" :class="{'highlights-loading': loadingRecords}")
      h1 {{ records.length }} articles found:
    h1(v-if="records.length == 0 && !loadingRecords") No results
    v-container(:class="{'highlights-loading': loadingRecords}")
      v-row(justify="center")
        v-pagination(
          v-model="pageNumber"
          :length="pageCount"
          :total-visible="10"
        )
      v-row(v-for="article in paginatedRecords" :key="article.id")
        v-col
          HighlightedListItem(:article="article")
      br
      v-row(justify="center")
        v-pagination(
          v-model="pageNumber"
          :length="pageCount"
          :total-visible="10"
        )
</template>

<script>
import HighlightedListItem from './list-item.vue'
import { mapGetters, mapState } from 'vuex'


export default {
  data() {
    return {
      pageNumber: 1,
      pageSize: 10
    }
  },
  components: {
    HighlightedListItem,
  },
  computed: {
    ...mapGetters('highlights', ['records']),
    ...mapState('highlights', ['loadingRecords']),
    pageCount() {
      let l = this.records.length,
          s = this.pageSize
      return Math.ceil(l / s)
    },
    paginatedRecords(){
      const start = (this.pageNumber - 1) * this.pageSize,
            end = start + this.pageSize;
      return this.records.slice(start, end);
}
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