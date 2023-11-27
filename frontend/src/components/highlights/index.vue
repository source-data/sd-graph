<template lang="pug">
div.d-flex.ml-auto.mr-auto
  v-container(v-if="loadingRecords")
    v-progress-circular(:size="70" :width="7" color="primary" indeterminate)

  span(v-if="!loadingRecords")
    v-container(fluid v-if="records.length > 0" :class="{'highlights-loading': loadingRecords}")
      h2 {{ records.length }} articles found
    v-container(fluid v-if="records.length == 0 && !loadingRecords")
      h2(v-if="records.length == 0 && !loadingRecords") No results
    v-container(fluid :class="{'highlights-loading': loadingRecords}")
      v-row(align="center" justify="start")
        v-col(cols=8).px-0.d-flex
          v-pagination(
            v-model="pageNumber"
            :length="pageCount"
            :total-visible="10"
          )
      v-row
        v-col.d-flex
          v-btn-toggle(v-model="sortBy" @change="sortRecords")
            v-tooltip(bottom)
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" outlined value="pub_date")
                  | preprint date
              span Sort by preprint date
            v-tooltip(bottom)
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small outlined value="posting_date" v-bind="attrs" v-on="on")
                  | reviewing date
              span Sort by revewing date

          v-btn-toggle(v-model="sortDirection" @change="sortRecords" mandatory).ml-3
            v-tooltip(right)
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" icon aria-label="descending" value="desc")
                  v-icon(dense) mdi-sort-descending
              span Show latest first
            v-tooltip(right)
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" icon aria-label="ascending" value="asc")
                  v-icon(dense) mdi-sort-ascending
              span Sort earliest first

      v-row(v-for="article in paginatedRecords" :key="article.id")
        v-col
          HighlightedListItem(:article="article")
      v-row(justify="start")
        v-col(cols=6).px-0.d-flex
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
      pageSize: 10,
    }
  },
  components: {
    HighlightedListItem,
  },
  computed: {
    ...mapGetters('highlights', ['records', 'selectedTab']),
    ...mapState('highlights', ['loadingRecords']),
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
    },
    sortBy: {
      get() {
        return this.$store.getters['highlights/getSortBy']
      },
      set(value) {
        this.$store.commit('highlights/setSortBy', {value: value})
      }
    },
    sortDirection: {
      get() { 
        return this.$store.getters['highlights/getSortDirection']
      },
      set(value) {
        this.$store.commit('highlights/setSortDirection', {value: value})
      }
    }
  },
  methods: {
    sortRecords() {
      this.$store.commit('highlights/setSortBy', {value: this.sortBy})
      this.$store.commit('highlights/setSortDirection', {value: this.sortDirection})
      this.$store.commit('highlights/sortRecords')
    },
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