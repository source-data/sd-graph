<template lang="pug">
  div
    el-row(type="flex" class="row-bg" justify="space-between")
      el-col
        h1 Results
      el-col
        p(v-if="selectedTab==='byReviewingService'")
          small Sort by: 
          el-radio-group(v-model="sortBy" size="mini" @change="sortRecords")
            el-radio-button(label="pub_date")
              | preprint date
            el-radio-button(label="posting_date")
              | reviewing date
          el-switch(
            style="margin-left:10px"
            v-model="sortDirection"
            @change="sortRecords"
            active-icon-class="el-icon-sort-up"
            active-value="asc"
            active-color="#409EFF"
            inactive-icon-class="el-icon-sort-down"
            inactive-value="desc"
            inactive-color="#409EFF"
          )
    div(v-if="records.length > 0")
        HighlitedListItem(:article="article" v-for="article in records")
    div(v-else)
        p No results
</template>

<script>
import HighlitedListItem from './list-item.vue'
import { mapGetters } from 'vuex'


export default {
  data () {
    return {
      sortBy: 'posting_date',
      sortDirection: 'desc',
    }
  },
  components: {
    HighlitedListItem,
  },
  methods: {
    sortRecords() {
      this.$store.commit('highlights/setSortBy', {value: this.sortBy})
      this.$store.commit('highlights/setSortDirection', {value: this.sortDirection})
      this.$store.commit('highlights/sortRecords')
    },
  },
  computed: {
    ...mapGetters('highlights', ['records', 'selectedTab']),
  },
}
</script>

<style>
/* needs to be in parent component */
 .md-content {
    max-height:350px; 
    overflow: scroll;
  }
  .md-content img {
    max-height: 60px;
  }
</style>