<template lang="pug">
  div
    h1 Search
    el-form(:inline="true" :model="search")
      el-form-item
        el-input(v-model="search.input" placeholder="keywords, authors, doi" clearable=true prefix-icon="el-icon-search")
      el-form-item
        el-button(type="primary" @click="onSubmit") Search
</template>

<script>

export default {
  data: function() {
    return {
      search: {
        input: '',
      } 
    }
  },
  methods: {
    onSubmit()  {
      this.$emit('submit', this.search.input)
    },
  }
}
</script>