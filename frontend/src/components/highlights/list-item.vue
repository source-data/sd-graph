<template lang="pug">
  v-card(
    v-if="article"
    class="pa-5"
    color="blue-grey lighten-5"
  )
    v-card-title
      | {{ article.title }}
      router-link(:to="`/doi/${article.doi}`")
        v-icon(color="indigo lighten-3") mdi-link-variant
    v-card-subtitle
      p {{ authorList }}
      p
        | Posted
        |
        b {{ displayDate(article.pub_date) }}
        |  on
        |
        i {{ serviceId2Name(article.journal) }}
      p
        b doi:
        a(:href="href(article.doi)" target="_blank" rel="noopener")
          |
          | https://doi.org/{{ article.doi }}
    v-card-text
      v-expansion-panels(v-if="article.review_process" focusable)
        v-expansion-panel(v-for="(review, i) in article.review_process.reviews" :key="i")
          v-expansion-panel-header()
            div(v-if="review.highlight")
              v-tooltip(
                v-if="review.highlight"
                top
                max-width="500px"
              )
                template(v-slot:activator="{ on, attrs }")
                  span(text v-bind="attrs" v-on="on")
                    v-icon(small class="px-1" color="indigo lighten-3") mdi-text-box-check-outline
                    |   Reviewed by
                    |
                    i {{ serviceId2Name(review.reviewed_by) }}
                    |  | Reviewer #
                    | {{ review.review_idx }}
                    | ({{ displayDate(review.posting_date) }})
                b Significance
                p {{ review.highlight }}
                b Click on tab to read full review.
            div(v-else)
              span
                v-icon(small class="px-1" color="indigo lighten-3") mdi-text-box-check-outline
                |   Reviewed by
                |
                i {{ serviceId2Name(review.reviewed_by) }}
                |  | Reviewer #
                | {{ review.review_idx }}
                | ({{ displayDate(review.posting_date) }})
          v-expansion-panel-content
            p(v-html="mdRender(review.text)").md-content
        v-expansion-panel(v-if="article.review_process.response" focusable)
          v-expansion-panel-header
            span
              v-icon(small class="px-1" color="indigo lighten-3") mdi-message-text-outline
              |   Response to the Reviewers
          v-expansion-panel-content
            p(v-html="mdRender(article.review_process.response.text)").md-content
        v-expansion-panel(v-if="article.review_process.annot")
          v-expansion-panel-header
            span
              v-icon(small class="px-1" color="indigo lighten-3") mdi-text-box-check-outline
              |  Reviewed by
              i  {{ serviceId2Name(article.review_process.annot.reviewed_by) }}
              |  | Review Process File
              | ({{ displayDate(article.review_process.annot.posting_date) }})
          v-expansion-panel-content
            p(v-html="mdRender(article.review_process.annot.text)").md-content
      v-expansion-panels(v-if="article.journal_doi")
        .v-expansion-panel
          .v-expansion-panel-header
            span
              v-icon(small class="px-1" color="indigo lighten-3") mdi-certificate-outline
              | Published in:
              i  {{ article.published_journal_title }}
              b  doi:
              a(:href="href(article.journal_doi)" target="_blank" rel="noopener")  https://doi.org/{{ article.journal_doi }}

      v-row
        v-col
          v-card
            v-card-title Abstract
            v-card-text
              p(class="text--primary") {{ article.abstract }}
        v-col
          v-expansion-panels(multiple v-model="activeCards" )
            v-expansion-panel(v-if="article.assays.length > 0" :key="0")
              v-expansion-panel-header Assays & Methods
              v-expansion-panel-content
                v-chip(v-for="(item, index) in article.assays" small outlined :key="`assay-text-${index}`").blue-grey--text {{ item }}
            v-expansion-panel(v-if="article.entities.length > 0" :key="1")
              v-expansion-panel-header Entities
              v-expansion-panel-content
                v-chip(v-for="(item, index) in article.entities" small outlined :key="`entities-text-${index}`").amber--text.text--darken-3 {{ item }}
</template>

<script>
import MarkdownIt from 'markdown-it'
import { serviceId2Name } from '../../store/by-reviewing-service'

export default {
  props: {
    article: Object,
  },
  data() {
    return {
      activeCards: [0,1],
    }
  },
  methods: {
    href(doi) {
      return new URL(doi,"https://doi.org/").href
    },
    displayDate(date_str) {
        // date_str needs to be in ISO 8601 format for Safari; YYYY-M-DD instead of YYYY-MM-DD will NOT work!
        const date = new Date(date_str)
        const year = date.getFullYear()
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const month = months[date.getMonth()]
        const day = date.getDate()
        return month + ' ' + day + ', ' + year
    },
    mdRender(md_text) {
      const md = new MarkdownIt({
          html: true,
          linkify: true,
          typographer: true
      })
      return md.render(md_text)
    },
    serviceId2Name,
    mapRole(role) {
      const map = {
        'intervention': 'danger',
        'assayed': '',
        'reporter': 'success',
        'normalizing': 'info',
        'experiment': 'danger',
        'component': 'warning'
      }
      const type = role in map? map[role] : 'info'
      return type
    }
  },
  computed: {
    authorList () {
      return this.article.authors.map(author => `${author.surname?author.surname+' ':''}${author.given_names?author.given_names:''}${author.collab?author.collab:''}${(author.corresp=='yes'?'*':'')}`).join(', ')
    },
    info () {
      return this.article.info
    },
  },
}
</script>

<style scoped>


  .md-content {
    font-family:'Courier New', Courier, monospace;
    font-size: 14px;
    max-height:800px;
    overflow: scroll;
  }
  .md-content img {
    max-height: 60px;
  }

  .fig-img {
    max-width: 300px;
    max-height: 300px;
  }
  .v-card__text, .v-card__title { /* bug fix; see https://github.com/vuetifyjs/vuetify/issues/9130 */
    word-break: normal; /* maybe !important  */
  }
</style>
