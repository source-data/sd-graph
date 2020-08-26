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
  metaInfo () {
    if (!this.article) {
      return {
        title: undefined,
      }
    }
    return {
      title: this.article.title,
      meta: [
        {
          vmid: 'description',
          name: 'description',
          content: this.article.abstract
        },
      ],
    }
  },
  data () {
    return {
      article: undefined,
      article_doi: undefined,
    }
  },
  methods: {
    getArticle (doi) {
      httpClient.get(`/api/v1/doi/${doi}`).then((response) => {
        let article = response.data[0]
        if (article.doi) {  // if the backend doesn't find the article it
                            // returns an article with all its properties set to null
          this.article = article
          return httpClient.get(`/api/v1/review/${doi}`)
        }
      })
      .then((response) => {
        if (response.data[0]) {
          let review_process = response.data[0].review_process
          this.article.review_process = review_process
        }
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
    this.getArticle(to.params.doi)
    next()
  },
}
</script>