<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Automatic selection of preprints
    v-card-text
      | Preprints are prioritized based on a combination of: 1) time of posting, 2) links to peer review, 3) multiplicity of approaches and topics
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
