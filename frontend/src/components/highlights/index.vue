<template lang="pug">
div(style="max-width: 100%;").d-flex.mr-auto.ml-auto
  v-container(v-if="loadingRecords").mt-6
    v-progress-circular(:size="70" :width="7" color="primary" indeterminate).ml-auto

  span(v-else style="max-width:100%;").mt-3
    v-container(fluid v-if="paging.totalItems > 0" :class="{'highlights-loading': loadingRecords}")
      h2 {{ $t('article_list.gt_0.title', {n: paging.totalItems}) }}
    v-container(fluid v-if="paging.totalItems == 0")
      h2 {{ $t('article_list.eq_0.title') }}
      p {{ $t('article_list.eq_0.subtitle') }}
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
        v-col.sort-controls.d-flex.flex-wrap.flex-column.flex-sm-row
          .input-group.d-flex.justify-space-between.justify-sm-start.flex-grow-1.flex-sm-grow-0
            label {{ $t('article_list.sort.by.label') }}
            v-btn-toggle(v-model="sortBy" mandatory).ml-1
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-btn(small v-bind="attrs" v-on="on" outlined value="preprint-date") {{ $t('article_list.sort.by.preprint_date.label') }}
                span {{ $t('article_list.sort.by.preprint_date.tooltip') }}
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-btn(small outlined value="reviewing-date" v-bind="attrs" v-on="on") {{ $t('article_list.sort.by.reviewing_date.label') }}
                span {{ $t('article_list.sort.by.reviewing_date.tooltip') }}

          .input-group.d-flex.justify-space-between.justify-sm-start.flex-grow-1.flex-sm-grow-0
            label {{ $t('article_list.sort.order.label') }}
            v-btn-toggle(v-model="sortedOrder" mandatory).ml-1
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-btn(small v-bind="attrs" v-on="on" outlined value="desc") {{ $t('article_list.sort.order.desc.label') }}
                span {{ $t('article_list.sort.order.desc.tooltip') }}
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-btn(small v-bind="attrs" v-on="on" outlined value="asc") {{ $t('article_list.sort.order.asc.label') }}
                span {{ $t('article_list.sort.order.asc.tooltip') }}

      v-row(v-if="paging.totalItems > 0")
        v-switch(v-model="openAbstracts" dense :label="$t('article_list.collapse_abstracts')").pl-3.mt-0

      v-row(v-for="article in records" :key="article.id")
        v-col(cols=12)
          HighlightedListItem(:article="article" :open-preprint-boxes="openedByDefault" :open-reviewed-boxes="[0, 1]")
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
.sort-controls {
  gap: 1rem;
}
</style>