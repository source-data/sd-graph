<template lang="pug">
v-card(v-if="article" color="tertiary")
  v-card-title.pb-3
    span.d-flex.flex-row
      router-link(:to="generateInternalUrl").paper-title
        p(style="vertical-align:baseline;") {{ article.title }}
      v-menu(close-on-click='' transition='slide-y-transition')
        template(v-slot:activator='{ on, attrs }')
          v-btn(color="primary" v-ripple="false" v-bind="attrs" v-on="on" depressed plain icon).ml-1.pb-2
            v-icon mdi-share-variant
        v-list(dense flat outlined)
          v-list-item
            v-list-item-title
              v-btn(@click="copyToClipboard(getFullStandaloneDoiUrl)" elevation=0 plain depressed v-ripple="false")
                v-icon(color="primary") mdi-link-variant
                span.ml-1 Copy link to clipboard
          v-list-item
            v-list-item-title
              v-btn(@click="copyToClipboard(citationText(true))" elevation=0 plain depressed v-ripple="false")
                v-icon(color="primary") mdi-content-copy
                span.ml-2 Copy citation
          v-list-item
            v-list-item-title
              v-btn(elevation=0 plain depressed v-ripple="false")
                a(:href="getTweetHref" target="_blank")
                  v-icon(color="gray") mdi-twitter
                  span.ml-2 Share on X
      
  v-card-subtitle.pb-1
    p.mb-0 {{ authorList }}

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
  v-card-text
    v-expansion-panels(accordion multiple v-model="dataOpenPreprintBoxes").mb-3.mt-1
      v-expansion-panel(mandatory eager)
        v-expansion-panel-header(color="tertiary")
            span
              h3.mb-1 Abstract
              span.sample-text.hide-when-expanded.text-body-2 {{ preview(article.abstract) }}
        v-expansion-panel-content(color="tertiary")
          p(class="text--primary").text-body-1 {{ article.abstract }}

      v-expansion-panel(v-if="hasFigureKeywords")
        v-expansion-panel-header(color="tertiary")
          span.d-flex.align-center
            h3 Preprint figure keywords
            v-tooltip(color="tooltip" bottom transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-1
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span <!-- TODO: Explain what these are and what the colors mean -->
                h3 Keywords deduced from the figures. 
                p(style="max-width: 250px;") Green text means this, orange text means that...
      
        v-expansion-panel-content(color="tertiary")
          div.d-flex.align-center
            v-list-item.px-0
              span.d-flex.flex-column.no-pointer-events
                v-chip-group(v-if="article.main_topics.length > 0" :key="0" column)
                  v-chip(v-for="(item, index) in article.main_topics"  outlined :key="`topics-${index}`").purple--text {{ item.slice(0,3).join(", ") }}
                v-chip-group(v-if="article.highlighted_entities.length > 0" :key="1" column)
                  v-chip(v-for="(item, index) in article.highlighted_entities"  outlined :key="`highlighted-entities-${index}`").red--text {{ item }}
                v-chip-group(v-if="article.entities.length > 0" :key="2" column)
                  v-chip(v-for="(item, index) in article.entities"  outlined :key="`entities-${index}`").orange--text {{ item }}
                v-chip-group(v-if="article.assays.length > 0" :key="3" column)
                  v-chip(v-for="(item, index) in article.assays"  outlined :key="`assays-${index}`").green--text {{ item }}

    v-expansion-panels(accordion multiple v-model="dataOpenReviewedBoxes")
      v-expansion-panel(readonly)
        v-expansion-panel-header(hide-actions)
          span.d-flex.flex-column
            h3(style="color: black;") Preprint review timeline
            //- TODO: enable this when the functionality is ready
              //- v-tooltip(bottom transition="fade-transition")
              //-   template(v-slot:activator="{ on, hover, attrs }")
              //-     v-btn(@click="???" v-bind="attrs" v-on="on" icon elevation=0 plain depressed v-ripple="false")
              //-       v-icon(color="primary") mdi-download-circle
              //-   span Download all review data

            span.pb-0.d-flex.flex-row.align-center
              b.mr-3 Reviewed by
              v-bottom-sheet(v-model="dialog" eager inset)
                template(v-slot:activator="{ on, attrs }")
                  v-chip-group
                    v-chip(
                      v-ripple="false" small
                      color="secondary"
                      outlined
                      @click="selectReviewerInfo(source)"
                      v-bind="attrs"
                      v-on="on" v-for='source in article.reviewed_by')
                      img(v-if="imageFileName(source)" :src="require(`@/assets/partner-logos/` + imageFileName(source))" height="24px" :alt="serviceId2Name(source)").pa-1
                      span(v-else) {{ serviceId2Name(source) }}
                      v-icon(right small) mdi-information

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
        v-expansion-panel-content(eager).pt-0
          span.review-process.d-flex.align-start.justify-start
            render-rev-timeline(:ref='article.doi + "-rev-timeline"')

      v-expansion-panel(v-if="maybeReviewSummary")
        v-expansion-panel-header
          span
            span.d-flex.align-center
              h3 Automated summary of preprint reviews
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-card(flat color="transparent" v-on:click.stop v-bind="attrs" v-on="on").ml-1
                    v-icon(color="grey-lighten-1") mdi-information-outline
                p(style="max-width: 250px;")
                  | This summary was generated automatically using ChatGPT-4 based on the content of the reviews. 
                  | Currently, this feature is limited to Review Commons reviews.
                  | To access the full content of the original reviews, click on "Peer Review".
            span.sample-text.hide-when-expanded.text-body-2 {{ preview(maybeReviewSummary) }}
            
        v-expansion-panel-content(eager)
          p(class="text--primary").text-body-1 {{ maybeReviewSummary }}

      v-expansion-panel
        v-expansion-panel-header 
          span.d-flex.align-baseline
            h3 Cite reviewed preprint
            v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-card(@click="copyToClipboard(citationText(true))" v-on:click.stop v-bind="attrs" v-on="on" icon elevation=0 plain depressed v-ripple="false").pl-2
                    v-icon(color="primary") mdi-content-copy
                span Click to copy reviewed preprint citation
        v-expansion-panel-content
          span.d-flex.flex-row.align-top
            p(v-html="this.citationText(false)").mb-2.text-body-1
</template>

<script>
import MarkdownIt from 'markdown-it'
import { BASE_URL } from '../../lib/http'
import { serviceId2Name, normalizeServiceName } from '../../store/by-filters'
import '@source-data/render-rev'
import { parse as parseDocmaps } from '@source-data/render-rev/src/docmaps.js'
import { mapState, mapGetters } from 'vuex'
import InfoCardsReviewServiceSummaryGraph from '../helpers/review-service-summary-graph.vue'

export default {
  components: {
    InfoCardsReviewServiceSummaryGraph
  },
  props: {
    article: Object,
    expandedReview: Object,

    // Props for the expansion panels that should be opened by default, passed from the parent component
    openPreprintBoxes: Array,
    openReviewedBoxes: Array
  },
  data() {
    return {
      dataOpenPreprintBoxes: this.openPreprintBoxes,
      dataOpenReviewedBoxes: this.openReviewedBoxes,

      dialog: false,
      selectedSource: null,

      // We grab the review from the docmaps, as it's easier to work with it by not relying on the render-rev component
      maybeReviewSummary: null,
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
    copyToClipboard (text) {
      this.$store.commit("setSnack", { message: "Text copied to clipboard!", color: "gray" });
      return navigator.clipboard.writeText(text);
    },
    selectReviewerInfo(value) {
      this.selectedSource = value;
    },
    imageFileName(id) {
      const availableSourceLogos = require.context('../../assets/partner-logos/', true, /\.(svg|png|jpg)/).keys()

      let normalizedServiceName = normalizeServiceName(serviceId2Name(id))
      let filename = availableSourceLogos.find(i => i.includes(normalizedServiceName))
      if (filename)
        return filename.substring(2) // substring to remove the `./` part of the name
      else return null
    },
    preview(text) {
      return text.split(/\s+/).slice(0, 25).join(" ") + "...";
    },
    citationText(stripHtmlFormatting) {
      const date = new Date(this.article.pub_date)       
      const year = date.getFullYear()
      
      const reviewedByText = this.article.reviewed_by.map(r => "peer reviewed by <b><i>" + serviceId2Name(r) + "</i></b>").join(", ")

      let citationText = `${this.authorList} (${year}). ${this.article.title}. <b><i>${this.article.journal}</i></b> doi.org/${this.article.doi}, ${reviewedByText} ${this.getFullStandaloneDoiUrl}.`
      
      if (stripHtmlFormatting)
        return citationText.replace(/<[^>]*>?/gm, '')
      else 
        return citationText
    }
  },
  computed: {
    ...mapGetters('byFilters', ['reviewingService']),
    ...mapState(['snackMessage, snackColor']),

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
    getFullStandaloneDoiUrl() {
      return `${window.location.host}/doi/${this.article.doi}`
    },
    getTweetHref() {
      let tweetContent = this.getFullStandaloneDoiUrl
      let fullLink = "https://twitter.com/intent/tweet?text=" + tweetContent
      return fullLink
    },
  },
  mounted() {
    const doi = this.article.doi;
    const highlightDoi = this.expandedReview ? this.expandedReview.doi : null;
    fetch(`${BASE_URL}/api/v2/docmap/${doi}`)
      .then(response => response.json())
      .then(parseDocmaps)
      .then(reviewProcess => {
        let reviewWithSummary = reviewProcess.timeline.groups.map(g => g.items).flat().find(i => i.type === "reviews" && i.summaries.length > 0);
        if (reviewWithSummary)
          this.maybeReviewSummary = reviewWithSummary.summaries[0]

        const timeline = this.$refs[doi + "-rev-timeline"];
        timeline.reviewProcess = reviewProcess;
        timeline.highlightItem = highlightDoi;
        const md = new MarkdownIt({
          html: true,
          linkify: true,
          typographer: true
        });
        timeline.options = {
          renderMarkdown: src => md.render(src),
        };
      });
  }
}
</script>


<style lang="scss" scoped>
  ::v-deep .v-expansion-panel-header__icon {
    margin-bottom: auto !important;
    padding-top: 0.5rem;
    padding-left: 0.5rem;
  }

  .v-card__text, .v-card__title { /* bug fix; see https://github.com/vuetifyjs/vuetify/issues/9130 */
    word-break: normal; /* maybe !important  */
  }

  .review-process {
    --rr-timeline-summary-bg-color: white;
    --rr-timeline-summary-text-color: black;
    --rr-timeline-width: 100%;
    overflow-y: scroll;
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

  .sample-text {
    opacity: 0.6;
  }

  .v-expansion-panel-header--active .hide-when-expanded {
    display: none;
  }

  .v-expansion-panel-header:not(.v-expansion-panel-header--active) .hide-when-not-expanded {
    display: none;
  }

  .paper-title {
    letter-spacing: normal;
    line-height: normal;
  }
</style>
