<template lang="pug">
  div
    div(v-show="loadingRecords" )
      el-row
        el-col
          el-button(circle plain type="primary" :loading="true" style="position: absolute; right: 0; top: 10px;")
    div(:class="{'highlights-loading': loadingRecords}")
      div(v-if="records.length > 0")
        el-row(type="flex" class="row-bg" justify="space-between")
          el-col
            h1 {{ records.length }} results found:
      p(v-else) No results

      div(v-for="article in records")
        el-card.box-card(shadow="hover")
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