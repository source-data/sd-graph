<template lang="pug">
  v-container(fluid).pa-0
    v-btn(
      color="primary"
      fixed
      bottom
      right
      style="bottom: 75px;"
      fab @click="$vuetify.goTo(0)")
      v-icon mdi-arrow-up

    v-row(v-if="article")
      v-col.d-flex.align-center
        HighlightedListItem(:article="article" :open-preprint-boxes=[0, 1, 2] :open-reviewed-boxes=[0, 1]).ml-auto.mr-auto
    v-row(v-else)
      v-col
        v-card
          v-card-title(v-if="article_slug") {{ $t('single_article.not_found.slug') }}
          v-card-title(v-else v-html="$t('single_article.not_found.doi_html', {doi: article_doi})")
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
        {rel: 'canonical', href: this.generateMyUrl()}
      ] ,
      meta: [
        {vmid: 'description', name: 'description', content: this.article.abstract},
        {name: 'og:title', property: 'og:title', content: this.article.title},
        {name: 'og:site_name', property: 'og:site_name', content: 'Early Evidence Base'},
        {name: 'og:type', property: 'og:type', content: 'article'},
        {name: 'og:url', property: 'og:url', content: this.generateMyUrl()},
        {name: 'og:image', property: 'og:image', content: `${this.publicPath}/EMBO_logo.svg`},
        {name: 'og:description', property: 'og:description', content: this.article.abstract},

        // Twitter card
        {name: 'twitter:card', content: 'summary'},
        {name: 'twitter:site', content: this.publicPath},
        {name: 'twitter:title', content: this.article.title},
        {name: 'twitter:description', content: this.article.abstract},
        {name: 'twitter:creator', content: '@EarlyEvidenceBase'},
        {name: 'twitter:image:src', content: `${this.publicPath}/EMBO_logo.svg`},
      ],
    }
  },
  data () {
    return {
      article: undefined,
      article_doi: undefined,
      article_slug: undefined,
      publicPath: 'https://eeb.embo.org',
    }
  },
  methods: {
    getArticle (params) {
      let url = null;
      if (params.slug) {
        this.article_slug = params.slug
        url = `/api/v2/paper/?slug=${params.slug}`
      } else if (params.doi) {
        this.article_doi = params.doi
        url = `/api/v2/paper/?doi=${params.doi}`
      }
      httpClient.get(url).then((response) => {
        let article = response.data
        if (article.doi) {  // if the backend doesn't find the article it
                            // returns an article with all its properties set to null
          this.article = article
        }
      })
    },
    generateMyUrl () {
      if (this.article_slug) {
        return `${this.publicPath}/p/${this.article_slug}`
      }
      return `${this.publicPath}/doi/${this.article_doi}`
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
      vm.getArticle(to.params)
    })
  },
  beforeRouteUpdate (to, from, next) {
    this.getArticle(to.params)
    next()
  },
}
</script>

<style lang="scss" scoped>
  ::v-deep .container {
    padding: 0 !important;
  }
</style>