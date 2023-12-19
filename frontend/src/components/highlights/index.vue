<template lang="pug">
div(style="max-width: 100%;").d-flex.mr-auto.ml-auto
  v-container(v-if="loadingRecords").mt-6
    v-progress-circular(:size="70" :width="7" color="primary" indeterminate).ml-auto

  span(v-else style="max-width:100%;").mt-3
    v-container(fluid v-if="paging.totalItems > 0" :class="{'highlights-loading': loadingRecords}")
      h2 {{ paging.totalItems }} reviewed preprints found
    v-container(fluid v-if="paging.totalItems == 0")
      h2 Sorry, we couldn't find any results
      p Try changing some of the filter values
    v-container(fluid :class="{'highlights-loading': loadingRecords}")
      v-row(align="center" justify="start")
        v-col(cols=8).px-0.d-flex
          v-pagination(
            v-if="paging.totalItems > 0"
            v-model="pageNumber"
            :length="this.paging.totalPages"
            :total-visible="10"
          )
      v-row(v-if="paging.totalItems > 0")
        v-col.d-flex
          v-btn-toggle(v-model="sortBy" mandatory)
            v-tooltip(color="tooltip" bottom transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" outlined value="preprint-date")
                  | preprint date
              span Sort by preprint date
            v-tooltip(color="tooltip" bottom transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small outlined value="reviewing-date" v-bind="attrs" v-on="on")
                  | reviewing date
              span Sort by revewing date

          v-btn-toggle(v-model="sortedOrder" mandatory).ml-3
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" icon aria-label="descending" value="desc")
                  v-icon(dense) mdi-sort-descending
              span Show latest first
            v-tooltip(color="tooltip" right transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-btn(x-small v-bind="attrs" v-on="on" icon aria-label="ascending" value="asc")
                  v-icon(dense) mdi-sort-ascending
              span Sort earliest first
      v-row(v-if="paging.totalItems > 0")
        v-switch(v-model="openAbstracts" dense label="Collapse all abstracts").pl-3.mt-0

      v-row(v-for="article in records" :key="article.id")
        v-col(cols=12)
          HighlightedListItem(:article="article" :open-preprint-boxes="openedByDefault" :open-reviewed-boxes="[1]")
      v-row(v-if="paging.totalItems > 0" justify="start")
        v-col(cols=6).px-0.d-flex
          v-pagination(
            v-model="pageNumber"
            :length="this.paging.totalPages"
            :total-visible="10"
          )
</template>

<script>
import HighlightedListItem from './list-item.vue'
import { mapState } from 'vuex'

export default {
  data() {
    return {
      openAbstracts: false,
      openedByDefault: [0]
    }
  },
  components: {
    HighlightedListItem,
  },
  computed: {
    ...mapState('byFilters', ['records', 'query', 'paging', 'loadingRecords', "error"]),
    pageNumber: {
      get() {
        return parseInt(this.paging.currentPage)
      },
      set(value) {
        this.$store.commit("byFilters/setCurrentPage", value);
      }
    },
    sortBy: {
      get() {
        return this.paging.sortedBy
      },
      set(value) {
        this.$store.commit('byFilters/setSortedBy', value);
      }
    },
    sortedOrder: {
      get() { 
        return this.paging.sortedOrder
      },
      set(value) {
        this.$store.commit('byFilters/setSortedOrder', value);
      }
    }
  },
  watch: {
    openAbstracts(nv) {
      if (nv) {
        this.openedByDefault = []
      }
      else {
        this.openedByDefault = [0]
      }
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