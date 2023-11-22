<template lang="pug">

v-container(fluid).pa-0.ma-0
  v-row.pa-6
    Highlights

</template>


<script>
import Highlights from '../components/highlights/index.vue'

export default {
  name: 'search',
  components: {
    Highlights
  },
  beforeMount() {
    this.$store.commit('highlights/resetRecords')
  },
}
</script>
