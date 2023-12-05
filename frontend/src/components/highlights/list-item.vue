<template lang="pug">
v-card(v-if="article" color="tertiary")
  v-card-title
    div
      | {{ article.title }}
      router-link(:to="generateMyUrl()")
        v-icon(color="indigo lighten-3").ml-1 mdi-link-variant
  v-card-subtitle
    p.mb-0 {{ authorList }}

    div.d-flex.flex-row.align-center
      v-list-item.px-0
        span.d-flex.flex-row.no-pointer-events
          v-chip-group(v-if="article.main_topics.length > 0" :key="0" column)
            v-chip(v-for="(item, index) in article.main_topics" small outlined :key="`topics-${index}`").purple--text {{ item.slice(0,3).join(", ") }}
          v-chip-group(v-if="article.highlighted_entities.length > 0" :key="1" column)
            v-chip(v-for="(item, index) in article.highlighted_entities" small outlined :key="`highlighted-entities-${index}`").red--text {{ item }}
          v-chip-group(v-if="article.entities.length > 0" :key="2" column)
            v-chip(v-for="(item, index) in article.entities" small outlined :key="`entities-${index}`").orange--text {{ item }}
          v-chip-group(v-if="article.assays.length > 0" :key="3" column)
            v-chip(v-for="(item, index) in article.assays" small outlined :key="`assays-${index}`").green--text {{ item }}
        
        v-tooltip(bottom transition="fade-transition")
          template(v-slot:activator="{ on, hover, attrs }")
            span(v-bind="attrs" v-on="on")
                v-icon(color="grey-lighten-1") mdi-information-outline
          span <!-- TODO: Explain what these are and what the colors mean -->
            h3 Keywords deduced from the figures. 
            p(style="max-width: 200px;") Green text means this, orange text means that...

    p
      | Posted
      |
      b {{ displayDate(article.pub_date) }}
      |  on
      |
      i {{ article.journal }}
      |
      a(:href="href(article.doi)" target="_blank" rel="noopener" class="ml-2")
        |
        | doi.org/{{ article.doi }}

  v-card-text
    v-container(fluid).article-content
      //- Vertical 1-col layout with review process first, abstract second on smaller screens, horizontal 2-col layout
      //-  with abstract left, review process right on larger screens. Entities always at the bottom in single column.
      v-row(v-if="showReviewProcess")
        v-col(order="2" order-md="1" cols="12" md="7")
          v-card.article-card
            v-card-title Abstract
            v-card-text
              p(class="text--primary") {{ article.abstract }}

        v-col(order="1" order-md="2" cols="12" md="5")
          div.review-process
            render-rev(:ref='article.doi')
      v-row(v-else)
        v-col
          v-card.article-card
            v-card-title Abstract
            v-card-text
              p(class="text--primary") {{ article.abstract }}
</template>

<script>
import MarkdownIt from 'markdown-it'
import { BASE_URL } from '../../lib/http'
import { serviceId2Name } from '../../store/by-filters'
import '@source-data/render-rev'

export default {
  props: {
    article: Object,
    expandedReview: Object,
  },
  data() {
    return {
      activeCards: [0,1,2],
    }
  },
  methods: {
    href(doi) {
      return new URL(doi, "https://doi.org/").href
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
    },
    reviewId(review) {
      return this.article.doi + '#rev0-pr' + review.review_idx
    },
    responseId() {
      return this.article.doi + '#rev0-ar'
    },
    generateMyUrl () {
      if (this.article.slug) {
        return `/p/${this.article.slug}`
      }
      return `/doi/${this.article.doi}`
    },
  },
  computed: {
    authorList() {
      // first, clone the authors array because sort() operates in-place on the array it's called on.
      const authorsSortedByPosition = this.article.authors.slice(0);
      function byPosition(a, b) {
        return a['position_idx'] - b['position_idx']
      }
      authorsSortedByPosition.sort(byPosition);
      return authorsSortedByPosition.map(author => `${author.surname ? author.surname + ' ' : ''}${author.given_names ? author.given_names : ''}${author.collab ? author.collab : ''}${(author.corresp == 'yes' ? '*' : '')}`).join(', ')
    },
    info () {
      return this.article.info
    },
    showReviewProcess() {
      return this.article.review_process && (
        this.article.review_process.reviews.length > 0
        || this.article.review_process.response
        || this.article.review_process.annot.length > 0
      )
    }
  },
  mounted() {
    if (this.showReviewProcess) {
      const docmapsUrl = doi => `${BASE_URL}/api/v2/docmap/${doi}`;
      const doi = this.article.doi;
      const highlightDoi = this.expandedReview ? this.expandedReview.doi : null;

      const md = new MarkdownIt({
        html: true,
        linkify: true,
        typographer: true
      });
      const display = {
        renderMarkdown: src => md.render(src),
      };

      const el = this.$refs[doi];
      el.configure({ docmapsUrl, doi, display, highlightDoi });
    }
  }
}
</script>

<style scoped>
  .v-card__text, .v-card__title { /* bug fix; see https://github.com/vuetifyjs/vuetify/issues/9130 */
    word-break: normal; /* maybe !important  */
  }

  .review-process {
    --rr-timeline-summary-bg-color: white;
    --rr-timeline-summary-text-color: black;
    --rr-timeline-width: 100%;
  }
  .v-sheet.v-card.article-card {
    box-shadow: unset;
    border-radius: 0;
  }

  @media screen and (max-width: 1080px) {
    .container.container--fluid.article-content {
      padding: 0;
    }
  }

  .v-chip.v-chip--outlined.v-chip.v-chip {
    background-color: white !important;
  }

  .no-pointer-events {
    pointer-events: none;
  }
</style>
