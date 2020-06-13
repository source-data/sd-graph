<template lang="pug">
  div
    HighlitedListItem(:article="article" v-for="article in records")
</template>

<script>
import HighlitedListItem from './list-item.vue'
import { mapGetters } from 'vuex'

export default {
  components: {
    HighlitedListItem,
  },
  computed: {
    ...mapGetters('highlights', ['records']),
  },
}
</script>