<template lang="pug">
  div
    h5 Search titles, abstracts, figure legends, authors or dois.
    .el-form.el-form--inline
      .el-form-item
        .el-form-item__content
          .el-input.el-input--prefix.el-input--suffix
            input.el-input__inner(v-model="query" placeholder="keywords, authors, doi", @keyup.enter="onSubmit")
            span.el-input__prefix
              i.el-input__icon.el-icon-search
      .el-form-item
        .el-form-item__content
          el-button(type="primary" @click="onSubmit") Search
</template>

<script>

export default {
  data: function() {
    return {
      query: ''
    }
  },
  methods: {
    onSubmit()  {
      console.log("submitting", this.query)
      this.$emit('submit', this.query)
    },
  }
}
</script>