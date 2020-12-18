<template lang="pug">
  div
    v-row(justify="center" v-if="loadingRecords")
      v-progress-circular(:size="70" :width="7" color="purple" indeterminate)
    div(v-else="loadingRecords")
    v-container(v-if="records.length > 0" :class="{'highlights-loading': loadingRecords}")
      h1 {{ records.length }} articles found:
    h1(v-if="records.length == 0 && !loadingRecords") No results
    v-container(:class="{'highlights-loading': loadingRecords}")
      v-row(align="center" justify="start")
        v-col(cols=1)
           .text-right 
             small Pages:
        v-col(cols=6)
          v-pagination(
            v-model="pageNumber"
            :length="pageCount"
            :total-visible="10"
          )
        v-col(cols=1 v-if="selectedTab == REFEREED_PREPRINTS")
          .text-right 
            small.text-right Sort by:
        v-col(cols=2 v-else)
           small.text-right Sort direction:
        v-col(cols=3 v-if="selectedTab == REFEREED_PREPRINTS" )
          v-btn-toggle(v-model="sortBy" @change="sortRecords")
            v-btn(x-small outlined value="pub_date")
              | preprint date
            v-btn(
              x-small outlined value="posting_date")
              | reviewing date
        v-col(cols=1)
          v-btn-toggle(v-model="sortDirection" @change="sortRecords" mandatory)
            v-btn(x-small icon value="desc")
              v-icon(dense) mdi-sort-descending
            v-btn(x-small icon value="asc")
              v-icon(dense) mdi-sort-ascending
      v-row(v-for="article in paginatedRecords" :key="article.id")
        v-col
          HighlightedListItem(:article="article")
      v-row(justify="start")
        v-col(cols=1)
           .text-right Pages:
        v-col(cols=6)
          v-pagination(
            v-model="pageNumber"
            :length="pageCount"
            :total-visible="10"
          )
</template>

<script>
import HighlightedListItem from './list-item.vue'
import { REFEREED_PREPRINTS } from '../quick-access/tab-names'
import { mapGetters, mapState } from 'vuex'


export default {
  data() {
    return {
      pageSize: 10,
      sortDirection: 'desc',
    }
  },
  components: {
    HighlightedListItem,
  },
  computed: {
    ...mapGetters('highlights', ['records', 'selectedTab']),
    ...mapState('highlights', ['loadingRecords']),
    refereedPreprintsTabName () {
      return REFEREED_PREPRINTS
    },
    pageNumber: {
      get() {
        return this.$store.getters['highlights/currentPage']
      },
      set(page) {
        this.$store.commit('highlights/updateCurrentPage', page)
      } 
    },
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
  methods: {
    sortRecords() {
      this.$store.commit('highlights/setSortBy', {value: this.sortBy})
      this.$store.commit('highlights/setSortDirection', {value: this.sortDirection})
      this.$store.commit('highlights/sortRecords')
    },
  },
  beforeUpdated() {
    console.debug("beforeUpdated", this.pageNumber)
  }
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