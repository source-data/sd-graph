<template lang="pug">
v-text-field(
  v-model="query"
  :loading="loadingRecords"
  placeholder="keywords, authors, doi"
  prepend-icon="mdi-magnify"
  hide-details
  @keyup.enter="onSubmit"
)
</template>

<script>
import { mapState } from 'vuex'
export default {
  data: function() {
    return {
      query: ''
    }
  },
  computed: {
    ...mapState('fulltextSearch', ['loadingRecords'])
  },
  methods: {
    onSubmit()  {
      this.$store.dispatch('fulltextSearch/search', this.query).then(
        () => {this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')}
      )
    },
  }
}
</script>
