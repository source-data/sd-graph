<template lang="pug">
    v-card(
      v-if="article"
      class="pa-5"
      color="blue-grey lighten-5"
    )
      v-row()
        v-col(:cols="12")
            h3
              | {{ article.title }}
              |
              router-link(:to="`/doi/${article.doi}`")
                v-icon(color="indigo lighten-3") mdi-link-variant
            p
              small
                | Posted
                |
                b {{ displayDate(article.pub_date) }}
                |  on
                |
                i {{ serviceId2Name(article.journal) }}
            p
              small
                b doi:
                a(:href="href(article.doi)" target="_blank" rel="noopener")  https://doi.org/{{ article.doi }}
            p
              small {{ authorList }}
            div(v-if="article.review_process")
              v-expansion-panels(focusable)
                v-expansion-panel(v-for="review in article.review_process.reviews")
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
                        p {{ review.highlight }}
                        b Click on tab to read full review.
                    div(v-else)
                      span.peer_review_material
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

      v-row(justify="space-between")
        v-col(:cols="6")
          p
            small(style="line-height:1.5") {{ article.abstract }}
          p
            small(style="font-family: monospace; font-size: 9px") [source: {{ article.source }}]
        v-col(:cols="6").scroll
          //- label(for="info-cards" style="font-variant: small-caps") {{ info.length }} information card{{ info.length > 1 ? 's':''}}:
          v-expansion-panels
            v-expansion-panel(v-for="(card, index) in info" id="infor-cards" v-model="activeCards" :value="index")
              v-expansion-panel-header {{ card.title }}
              v-expansion-panel-content(v-if="card.entities.length > 1" )
                  p
                    span(v-for="entity in card.entities")
                      v-chip(small :type="mapRole(entity.role)") {{ entity.text }}
                  p(v-if="card.id")
                    a(target="_blank" rel="noopener" :href="`https://search.sourcedata.io/panel/${card.id}`")
                      img(:src="`https://api.sourcedata.io/file.php?panel_id=${card.id}`").fig-img
                    br
                    a(target="_blank" rel="noopener" :href="`https://search.sourcedata.io/panel/${card.id}`")
                      | open as SmartFigures
              v-expansion-panel-content(v-else-if="card.text instanceof Array")
                v-chip(v-for="item in card.text" small) {{ item }}
              v-expansion-panel-content(v-else="typeof card.text === 'string'")
                small(style="line-height:1.3") {{ card.text }}
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
        // .panel_ids.map((panel_id) => {
        //   return {
        //     id: panel_id,
        //     img_url: `https://api.sourcedata.io//file.php?panel_id=${panel_id}`,
        //     url: `https://search.sourcedata.io/panel/${panel_id}`,
        //   }
        // })
    },
  },
}
</script>

<style scoped>
  .scroll {
    max-height: 500px;
    overflow: auto;
  }
  .fig-img {
    max-width: 300px;
    max-height: 300px;
  }

</style>
