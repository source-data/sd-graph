<template lang="pug">
  v-footer(padless).d-flex.flex-grow-1
    router-link(to="/about")
      v-list-item(index="1")
        span About
    router-link(to="/contact")
      v-list-item(index="3")
        span Contact
    v-spacer 
    a(href="https://github.com/source-data/sd-graph" target="_blank" rel="noopener").pr-2.ml-auto.mr-2
      img(src="../assets/github-mark.png" alt="EMBO Logo").gh-badge
    span EMBO &#169; {{ thisYear }}
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
  },
}
</script>

<style>
.gh-badge {
  width:35px;
}
</style>