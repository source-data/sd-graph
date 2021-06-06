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
      link: [
        {rel: 'canonical', href: `https://eeb.embo.org/doi/${this.article_doi}`}
      ] ,
      meta: [
        {vmid: 'description', name: 'description', content: this.article.abstract},
        {property: 'og:title', content: this.article.title},
        {property: 'og:site_name', content: 'Early Evidence Base'},
        {property: 'og:type', content: 'article'},
        {property: 'og:url', content: `https://eeb.embo.org/doi/${this.article_doi}`},
        {property: 'og:image', content: 'https://eeb.embo.org/img/EEB_HP_Banner.286d8912.svg'},
        {property: 'og:description', content: this.article.abstract},

        // Twitter card
        {name: 'twitter:card', content: 'summary'},
        {name: 'twitter:site', content: 'https://www.my-site.com/my-special-page'},
        {name: 'twitter:title', content: this.article.title},
        {name: 'twitter:description', content: this.article.abstract},
        {name: 'twitter:creator', content: '@EarlyEvidenceBase'},
        {name: 'twitter:image:src', content: 'https://www.my-site.com/my-special-image.jpg'},

        // Google / Schema.org markup:
        {itemprop: 'name', content: this.article.title},
        {itemprop: 'description', content: this.article.abstract},
        {itemprop: 'image', content: 'https://eeb.embo.org/img/EEB_HP_Banner.286d8912.svg'}
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