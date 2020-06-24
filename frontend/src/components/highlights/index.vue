<template lang="pug">
  div
    el-row(type="flex" class="row-bg" justify="space-between")
      el-col
        h1 Results
      el-col
        small Sort by: 
        el-radio-group(v-model="sortBy" size="mini" @change="sortRecords")
          el-radio-button(label="pub_date")
            | publication date
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
    HighlitedListItem(:article="article" v-for="article in records")
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
      this.$store.commit('highlights/sortRecords', {
        sortBy: this.sortBy,
        direction: this.sortDirection,
      })
    },
  },
  computed: {
    ...mapGetters('highlights', ['records']),
  },
}
</script>