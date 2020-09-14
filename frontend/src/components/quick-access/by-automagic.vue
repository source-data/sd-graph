<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Preprints are prioritized by enriching for studies with a multiplicity of experimental approaches. 
</template>

<script>

export default {
  beforeMount(){
    this.$store.commit('highlights/setSortBy', {value: 'rank'})
    this.$store.commit('highlights/setSortDirection', {value: 'asc'})
    this.$store.commit('highlights/sortRecords')
  }
}
</script>
