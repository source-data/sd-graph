<template lang="pug">
  div
    div(v-if="loadingRecords")
      el-button(circle plain type="primary" :loading="true" size="normal")
    div(v-else="loadingRecords")
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
