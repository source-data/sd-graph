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
                span.ml-1 {{ $t('article.actions.copy.link') }}
          v-list-item
            v-list-item-title
              v-btn(@click="copyToClipboard(citationText(true))" elevation=0 plain depressed v-ripple="false")
                v-icon(color="primary") mdi-content-copy
                span.ml-2 {{ $t('article.actions.copy.citation') }}
          v-list-item
            v-list-item-title
              v-btn(elevation=0 plain depressed v-ripple="false")
                a(:href="getTweetHref" target="_blank")
                  v-icon(color="gray") mdi-twitter
                  span.ml-2 {{ $t('article.actions.share.x') }}
      
  v-card-subtitle.pb-1
    p.mb-0 {{ authorList }}

    span(v-html="$t('article.info.posted_on', {date: displayDate(article.pub_date), server: article.journal, url: href(article.doi), doi: article.doi})")
  v-card-text
    v-expansion-panels(accordion multiple v-model="dataOpenPreprintBoxes").mb-3.mt-1
      v-expansion-panel(mandatory eager)
        v-expansion-panel-header(color="tertiary")
            span
              h3.mb-1 {{ $t('article.abstract.title') }}
              span.sample-text.hide-when-expanded.text-body-2 {{ preview(article.abstract) }}
        v-expansion-panel-content(color="tertiary")
          p(class="text--primary").text-body-1 {{ article.abstract }}

      v-expansion-panel(v-if="hasFigureKeywords")
        v-expansion-panel-header(color="tertiary")
          span.d-flex.align-center
            h3 {{ $t('article.figure_keywords.title') }}
            v-tooltip(color="tooltip" bottom transition="fade-transition")
              template(v-slot:activator="{ on, hover, attrs }")
                v-card(color="transparent" flat v-on:click.stop v-bind="attrs" v-on="on").ml-1
                  v-icon(color="grey-lighten-1") mdi-information-outline
              span <!-- TODO: Explain what these are and what the colors mean -->
                h3 {{ $t('article.figure_keywords.info.title') }}
                p(style="max-width: 250px;") {{ $t('article.figure_keywords.info.message') }}
      
        v-expansion-panel-content(color="tertiary")
          div.d-flex.align-center
            v-list-item.px-0
              span.d-flex.flex-column.no-pointer-events
                v-chip-group(v-if="article.entities.length > 0" :key="2" column)
                  v-chip(v-for="(item, index) in article.entities"  outlined :key="`entities-${index}`").orange--text {{ item }}
                v-chip-group(v-if="article.assays.length > 0" :key="3" column)
                  v-chip(v-for="(item, index) in article.assays"  outlined :key="`assays-${index}`").green--text {{ item }}

    v-card.no-bottom-radius
      v-card-title 
        span.d-flex.flex-column
          h4(style="color: black;") {{ $t('article.reviews.title') }}
          //- TODO: enable this when the functionality is ready
            //- v-tooltip(bottom transition="fade-transition")
            //-   template(v-slot:activator="{ on, hover, attrs }")
            //-     v-btn(@click="???" v-bind="attrs" v-on="on" icon elevation=0 plain depressed v-ripple="false")
            //-       v-icon(color="primary") mdi-download-circle
            //-   span Download all review data
      v-card-subtitle
          span.pb-0.d-flex.flex-row.align-center
            b.mr-3 {{ $t('article.reviews.peer_reviewed_by') }}
            v-bottom-sheet(v-model="dialog" eager inset)
              template(v-slot:activator="{ on, attrs }")
                v-chip-group
                  v-chip(
                    v-ripple="false" small
                    color="secondary"
                    outlined
                    @click="selectReviewerInfo(source)"
                    v-bind="attrs"
                    v-on="on"
                    v-for='source in article.reviewed_by'
                    :key="source")
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
                :opportunity_for_author_response="reviewingService(selectedSource).opportunity_for_author_response",
                :recommendation="reviewingService(selectedSource).recommendation",
              ).px-0.mt-2
      v-card-text
        span.review-process.d-flex.align-start.justify-start
          render-rev-timeline.d-md-none(ref="render-rev-timeline")
          render-rev-timeline-horizontal.d-none.d-md-block(ref="render-rev-timeline-horizontal")

    v-expansion-panels(accordion multiple v-model="dataOpenReviewedBoxes").no-top-radius
      v-expansion-panel(v-if="maybeReviewSummary")
        v-expansion-panel-header
          span
            span.d-flex.align-center
              h3 {{ $t('article.reviews.summary.title') }}
              v-tooltip(color="tooltip" bottom transition="fade-transition")
                template(v-slot:activator="{ on, hover, attrs }")
                  v-card(flat color="transparent" v-on:click.stop v-bind="attrs" v-on="on").ml-1
                    v-icon(color="grey-lighten-1") mdi-information-outline
                p(style="max-width: 250px;") {{ $t('article.reviews.summary.info.message') }}
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
                span {{ $t('article.cite.btn.tooltip') }}
        v-expansion-panel-content
          span.d-flex.flex-row.align-top
            p(v-html="this.citationText(false)").mb-2.text-body-1
</template>

<script>
import MarkdownIt from 'markdown-it'
import { serviceId2Name, normalizeServiceName } from '../../store/by-filters'
import '@source-data/render-rev'
import { mapGetters, mapState } from 'vuex'
import InfoCardsReviewServiceSummaryGraph from '../helpers/review-service-summary-graph.vue'

export default {
  components: {
    InfoCardsReviewServiceSummaryGraph
  },
  props: {
    article: Object,

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

      reviewProcess: null,
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
      this.$store.commit("setSnack", { message: "snack.message.copied", color: "gray" });
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

      const reviewedByText = this.article.reviewed_by.map(r => this.$t('article.cite.text.reviewed_by', {service: serviceId2Name(r)})).join(", ")

      let citationText = this.$t('article.cite.text.citation', {
        authors: this.authorList,
        year,
        title: this.article.title,
        journal: this.article.journal,
        doi: this.article.doi,
        reviewedBy: reviewedByText,
        reviewedPreprintUrl: this.getFullStandaloneDoiUrl,
      })
      if (stripHtmlFormatting)
        return citationText.replace(/<[^>]*>?/gm, '')
      else 
        return citationText
    },
    updateReviewTimeline() {
      const timelines = [this.$refs["render-rev-timeline"], this.$refs["render-rev-timeline-horizontal"]];
      for (let timeline of timelines) {
        timeline.highlightItem = this.expandedReview;
        timeline.options = this.timelineOptions;
        timeline.reviewProcess = this.reviewProcess;
      }
    },
  },
  computed: {
    ...mapGetters('byArticleId', ['getReviewProcessForDoi']),
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
    expandedReview() {
      let hash = this.$route.hash;
      if (!hash) {
        return undefined;
      }

      // restricted to RC reviews for now
      const group = this.reviewProcess.timeline.groups.find(group => group.publisher.name === "review commons")
      if (!group) {
        return undefined;
      }

      if (hash === '#rev0-ar') {  // expand response
        const item = group.items.find(item => item.type === "response");
        const content = item.contents[0];
        return {group, item, content};
      }

      const match = hash.match(/^#rev0-rr([0-9]+)$/);
      if (!match) {
        return undefined;
      }
      const reviewIdx = Number(match[1]) - 1;  // convert from 1- to 0-based indexing

      const item = group.items.find(item => item.type === "reviews");
      if (reviewIdx < 0 || reviewIdx >= item.contents.length) {
        return undefined;
      }
      const content = item.contents[reviewIdx];
      return {group, item, content};

    },
    info () {
      return this.article.info
    },
    hasFigureKeywords() {
      return this.article.entities.length > 0 || this.article.assays.length > 0
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
    maybeReviewSummary() {
      if (!this.reviewProcess) {
        return null;
      }
      let reviewWithSummary = this.reviewProcess.timeline.groups.map(g => g.items).flat().find(i => i.type === "reviews" && i.summaries.length > 0);
      if (!reviewWithSummary) {
        return null;
      }
      return reviewWithSummary.summaries[0]
    },
    timelineOptions() {
      return {
        renderMarkdown: src => this.mdRender(src),
      }
    },
  },
  watch: {
    openPreprintBoxes: function (newVal) {
      this.dataOpenPreprintBoxes = newVal
    },
  },
  created() {
    const doi = this.article.doi;
    this.$store.dispatch("byArticleId/fetchReviewProcessForDoi", doi).then(() => {
      this.reviewProcess = this.getReviewProcessForDoi(doi);
      this.updateReviewTimeline();
    });
  },
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

  .no-bottom-radius {
    border-radius: 4px 4px 0 0 !important;
  }

  .no-top-radius>:first-child {
    border-radius: 0 0 !important;
    border-top: 1px solid rgb(0, 0, 0, 0.1);
  }

</style>
