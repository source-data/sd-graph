<template lang="pug">
  div
    div(v-if="article")
      HighlitedListItem(:article="article")
    div(v-else="article")
      h1 The article with doi #[em {{ article_doi }}] was not found.

</template>

<script>
import httpClient from '../../lib/http'
import HighlitedListItem from './list-item.vue'

export default {
  name:'article-show',
  components: {
    HighlitedListItem,
  },
  data () {
    return {
      article: undefined,
      article_doi: undefined,
    }
  },
  methods: {
    getArticle (doi) {
      httpClient.get(`/api/v1/doi/${doi}`)
        .then((response) => {
          let article = response.data[0]
          if (!article.doi) {
            article = null
          }
          this.article = article
        })
    },
  },
  beforeRouteEnter (to, from, next) {
    next((vm) => {
      vm.article_doi = to.params.doi
      vm.getArticle(to.params.doi)
    })
  },
  beforeRouteUpdate (to, from, next) {
    this.article_doi = to.params.doi
    next()
  },
}
</script>