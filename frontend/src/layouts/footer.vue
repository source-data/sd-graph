<template lang="pug">
  el-row
    el-col(:span="16" :offset="4")
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
