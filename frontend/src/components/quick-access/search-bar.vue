<template lang="pug">
  v-card(class="pa-5" outlined)
    v-card-title Search titles, abstract, figure legends,author name, doi
    v-card-text
      v-container
        v-row()
          v-col()
            v-text-field(
              v-model="query"
              outlined
              clearable
              placeholder="keywords, authors, doi"
              prepend-icon="mdi-magnify"
              @keyup.enter="onSubmit"
            )
          v-col()
            v-btn(
              @click="onSubmit"
              color="primary"
            ) Search
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
      this.$emit('submit', this.query)
    },
  }
}
</script>