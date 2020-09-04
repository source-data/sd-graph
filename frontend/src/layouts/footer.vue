<template lang="pug">
  v-row()
    v-col(align="right")
      small EMBO 	&#169; {{ thisYear }}
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
