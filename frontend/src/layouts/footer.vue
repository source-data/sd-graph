<template lang="pug">
  v-row
    v-col.d-flex.flex-row
        router-link(to="/about")
          v-list-item(index="1")
            span About
        router-link(to="/for-developers")
          v-list-item(index="2")
            span For developers
        router-link(to="/contact")
          v-list-item(index="3")
            span Contact
    v-col.d-flex.align-center
      span.ml-auto EMBO &#169; {{ thisYear }}
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
