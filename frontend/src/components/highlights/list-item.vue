<template lang="pug">
v-card(v-if="article" color="tertiary")
  v-card-title
    div
      router-link(:to="generateInternalUrl").paper-title
        | {{ article.title }}

      v-tooltip(bottom transition="fade-transition")
        template(v-slot:activator="{ on, hover, attrs }")
          v-btn(@click="copyFullUrlToClipboard" v-bind="attrs" v-on="on" icon elevation=0 plain depressed v-ripple="false")
            v-icon(color="primary").ml-3 mdi-link-variant
        span Copy link to clipboard

      v-tooltip(bottom transition="fade-transition")
        template(v-slot:activator="{ on, hover, attrs }")
          v-btn(@click="copyCitationToClipboard" v-bind="attrs" v-on="on" icon elevation=0 plain depressed v-ripple="false")
            v-icon(color="primary").ml-1 mdi-format-quote-open
        span Copy formatted citation

      v-tooltip(bottom transition="fade-transition")
        template(v-slot:activator="{ on, hover, attrs }")
          a(v-bind="attrs" v-on="on" :href="getTweetHref")
            v-icon(color="primary").ml-1 mdi-twitter
        span Share on X
      
  v-card-subtitle
    p.mb-0 {{ authorList }}

    div(v-if="hasFigureKeywords").d-flex.flex-row.align-center
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

    span
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

    span.d-flex.flex-row.align-center
      span.mr-3 Reviewed by 
      v-bottom-sheet(v-model="dialog" inset)
        template(v-slot:activator="{ on, attrs }")
          v-chip-group
            v-chip(
              color="secondary"
              outlined
              @click="selectReviewerInfo(source)"
              v-bind="attrs"
              v-on="on" v-for='source in article.reviewed_by')
              | {{ serviceId2Name(source) }}
              v-icon(right) mdi-information

        InfoCardsReviewServiceSummaryGraph(
          :service_name="serviceId2Name(selectedSource)",
          :url="reviewingService(selectedSource).url",
          :peer_review_policy="reviewingService(selectedSource).peer_review_policy",
          :review_requested_by="reviewingService(selectedSource).review_requested_by",
          :reviewer_selected_by="reviewingService(selectedSource).reviewer_selected_by",
          :review_coverage="reviewingService(selectedSource).review_coverage",
          :reviewer_identity_known_to="reviewingService(selectedSource).reviewer_identity_known_to",
          :competing_interests="reviewingService(selectedSource).competing_interests",
          :public_interaction="reviewingService(selectedSource).public_interaction",
          :opportunity_for_author_response="reviewingService(selectedSource).opportunity_for_author_response",
          :recommendation="reviewingService(selectedSource).recommendation",
        ).px-0.mt-2

  v-card-text
    v-container(fluid).article-content
      //- Vertical 1-col layout with review process first, abstract second on smaller screens, horizontal 2-col layout
      //-  with abstract left, review process right on larger screens. Entities always at the bottom in single column.
      v-row
        v-col(order="2" order-md="1" cols="12" md="7")
          v-card.article-card
            v-card-title Abstract
            v-card-text
              p(class="text--primary") {{ article.abstract }}

        v-col(order="1" order-md="2" cols="12" md="5")
          div.review-process
            render-rev(:ref='article.doi')
</template>

<script>
import MarkdownIt from 'markdown-it'
import { BASE_URL } from '../../lib/http'
import { serviceId2Name } from '../../store/by-filters'
import '@source-data/render-rev'
import { mapGetters } from 'vuex'
import InfoCardsReviewServiceSummaryGraph from '../review-service-info/review-service-summary-graph.vue'

export default {
  components: {
    InfoCardsReviewServiceSummaryGraph
  },
  props: {
    article: Object,
    expandedReview: Object,
  },
  data() {
    return {
      dialog: false,
      selectedSource: null
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
    copyFullUrlToClipboard () {
      navigator.clipboard.writeText(window.location.host + this.generateInternalUrl);
    },
    copyCitationToClipboard () {
      navigator.clipboard.writeText(this.citationText);
    },
    selectReviewerInfo(value) {
      this.selectedSource = value;
    }
  },
  computed: {
    ...mapGetters('byFilters', ['reviewingService']),

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
    hasFigureKeywords() {
      return this.article.main_topics.length > 0 || this.article.highlighted_entities.length > 0 || 
        this.article.entities.length > 0 || this.article.assays.length > 0
    },
    generateInternalUrl () {
      if (this.article.slug) {
        return `/p/${this.article.slug}`
      }
      return `/doi/${this.article.doi}`
    },
    getFullStandaloneUrl() {
      return window.location.host + this.generateInternalUrl
    },
    getTweetHref() {
      let tweetContent = this.getFullStandaloneUrl
      let fullLink = "https://twitter.com/intent/tweet?text=" + tweetContent
      return fullLink
    },
    citationText() {
      const date = new Date(this.article.pub_date)       
      const year = date.getFullYear()
      
      const reviewedByText = this.article.reviewed_by.map(r => "peer reviewed by " + serviceId2Name(r)).join(", ")

      let citationText = `${this.authorList} (${year}). ${this.article.title}. ${this.article.journal} ${this.article.doi}, ${reviewedByText} ${this.getFullStandaloneUrl}.`
      return citationText
    }
  },
  mounted() {
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
    box-shadow: 0 3px 1px -2px rgba(0,0,0,.2), 0 2px 2px 0 rgba(0,0,0,.14), 0 1px 5px 0 rgba(0,0,0,.12);
    border-radius: 4px;
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

  .v-dialog > .v-card {
    margin: 0px !important;
    border-radius: 0;
  }

  a:hover {
    color: #217b90;
  }
</style>
