<template lang="pug">
  v-container
    v-row(v-if="article")
      v-col
        HighlightedListItem(:article="article")
    v-row(v-else="article")
      v-col
        v-card
          v-card-title 
            | The article with doi:
            |
            code {{ article_doi }}
            |
            | was not found.

</template>

<script>
import httpClient from '../../lib/http'
import HighlightedListItem from './list-item.vue'

export default {
  name:'article-show',
  components: {
    HighlightedListItem,
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