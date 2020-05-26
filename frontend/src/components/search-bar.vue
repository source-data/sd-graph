<template lang="pug">
  div
    h1 Search
    el-form(:inline="true" :model="search")
      el-form-item
        el-input(v-model="search.input" placeholder="enter search terms" clearable=true prefix-icon="el-icon-search")
      el-form-item
        el-button(type="primary" @click="onSubmit") Search
</template>

<script>

export default {
  data: function() {
    return {
      search: {
        input: '',
        somethignelse: ''
      } 
    }
  },
  methods: {
    onSubmit()  {
      console.debug('search', this.search.input),
      this.$store.dispatch('fulltextSearch/search', this.search.input).then(
        () => {
          this.$store.dispatch('highlights/listByCurrent', 'fulltextSearch')
        }
      )
    },
  }
}
</script>