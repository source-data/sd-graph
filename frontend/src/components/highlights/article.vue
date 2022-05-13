<template lang="pug">
  v-container
    v-row(v-if="article")
      v-col
        HighlightedListItem(:article="article" :expandedReview="expandedReview")
    v-row(v-else="article")
      v-col
        v-card
          v-card-title 
            | The article with doi:
            |
            code {{ article_doi }}
            |
            | was not found.
    div
      script(v-if="article" v-html="generate_jsonld(article)" type="application/ld+json")

</template>

<script>
import httpClient from '../../lib/http'
import HighlightedListItem from './list-item.vue'

export default {
  name:'article-show',
  components: {
    HighlightedListItem
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
        {rel: 'canonical', href: this.generateMyUrl(this.article_doi)}
      ] ,
      meta: [
        {vmid: 'description', name: 'description', content: this.article.abstract},
        {name: 'og:title', property: 'og:title', content: this.article.title},
        {name: 'og:site_name', property: 'og:site_name', content: 'Early Evidence Base'},
        {name: 'og:type', property: 'og:type', content: 'article'},
        {name: 'og:url', property: 'og:url', content: this.generateMyUrl(this.article_doi)},
        {name: 'og:image', property: 'og:image', content: `${this.publicPath}/EEB_E_LOGO.png`},
        {name: 'og:description', property: 'og:description', content: this.article.abstract},

        // Twitter card
        {name: 'twitter:card', content: 'summary'},
        {name: 'twitter:site', content: this.publicPath},
        {name: 'twitter:title', content: this.article.title},
        {name: 'twitter:description', content: this.article.abstract},
        {name: 'twitter:creator', content: '@EarlyEvidenceBase'},
        {name: 'twitter:image:src', content: `${this.publicPath}/EEB_E_LOGO.png`},
      ],
    }
  },
  data () {
    return {
      article: undefined,
      article_doi: undefined,
      publicPath: 'https://eeb.embo.org',
    }
  },
  computed: {
    expandedReview () {
      let hash = this.$route.hash;
      if (!hash) {
        return undefined;
      }

      /* If we want to expand the author response, return the number of reviews. The author response, if it exists, is
       * treated like an additional review internally, therefore its 0-based index is equal to the number of reviews.
       */
      let numReviews = this.article.review_process.reviews.length;
      if (hash === '#rev0-ar') {
        // Check if there even is an author response to expand...
        if (this.article.review_process.response != null) {
          return numReviews;
        }
        return undefined;
      }

      let match = hash.match(/^#rev0-rr([0-9]+)$/);
      if (!match) {
        return undefined;
      }

      let reviewIdx = Number(match[1]);
      if (reviewIdx <= 0 || reviewIdx > numReviews) {
        return undefined;
      }
      return reviewIdx - 1;
    },
  },
  methods: {
    getArticle (doi) {
      httpClient.get(`/api/v1/doi/${doi}`).then((response) => {
        let article = response.data[0]
        if (article.doi) {  // if the backend doesn't find the article it
                            // returns an article with all its properties set to null
          this.article = article
          // return httpClient.get(`/api/v1/review/${doi}`)
        }
      })
      // .then((response) => {
      //   if (response.data[0]) {
      //     let review_process = response.data[0].review_process
      //     this.article.review_process = review_process
      //   }
      // })
    },
    generateMyUrl (doi) {
      return `${this.publicPath}/doi/${doi}`
    },
    generateKeywords (article) {
      const assays = article.assays
      const topics = article.main_topics.length > 0 ? article.main_topics[0] : []
      const highlighted_entities = article.highlighted_entities
      const other_entities = article.entities
      const keywords = [].concat(assays, topics, highlighted_entities, other_entities)
      return keywords.join(", ")
    },
    generateAuthorList (article) {
      const authors = article.authors.map(a => {
        return {
          "@type": "Person",
          givenName: a.given_names,
          familyName: a.surname
        }
      })
      return authors
    },
    generate_jsonld (article) {
      const j= {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title,
        "image": [],
        "datePublished": article.pub_date,
        "author": this.generateAuthorList(article),
        "keywords": this.generateKeywords(article),
        "publisher": {
          "@type": "Organization",
          "name": "bioRxiv",
          "logo": {
            "@type": "ImageObject",
            "url": "https://www.biorxiv.org/sites/default/files/site_logo/bioRxiv_logo_homepage.png"
          }
        },
      }
      return j
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

