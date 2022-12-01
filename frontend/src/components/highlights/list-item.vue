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
      v-container(fluid)
        v-row
          v-col
            p {{ authorList }}
            p
              | Posted
              |
              b {{ displayDate(article.pub_date) }}
              |  on
              |
              i {{ article.journal }}
            p
              b doi:
              a(:href="href(article.doi)" target="_blank" rel="noopener")
                |
                | https://doi.org/{{ article.doi }}
          v-col
            render-rev(:doi='article.doi' :ref='article.doi')

    v-card-text
      v-row
        v-col
          v-card
            v-card-title Abstract
            v-card-text
              p(class="text--primary") {{ article.abstract }}
        v-col
          v-card(v-if="(article.assays.length > 0) || (article.entities.length > 0) || (article.highlighted_entities.length > 0)")
            v-card-title From the figures
            v-card-text
                v-list-item
                  v-chip-group(v-if="article.main_topics.length > 0" :key="0" column)
                    v-chip(v-for="(item, index) in article.main_topics" small outlined :key="`topics-${index}`").purple--text {{ item.slice(0,3).join(", ") }}
                  v-chip-group(v-if="article.highlighted_entities.length > 0" :key="1" column)
                    v-chip(v-for="(item, index) in article.highlighted_entities" small outlined :key="`highlighted-entities-${index}`").red--text {{ item }}
                  v-chip-group(v-if="article.entities.length > 0" :key="2" column)
                    v-chip(v-for="(item, index) in article.entities" small outlined :key="`entities-${index}`").orange--text {{ item }}
                  v-chip-group(v-if="article.assays.length > 0" :key="3" column)
                    v-chip(v-for="(item, index) in article.assays" small outlined :key="`assays-${index}`").green--text {{ item }}
          v-card(v-else)
            v-card-subtitle Figure not yet processed
</template>

<script>
import MarkdownIt from 'markdown-it'
import { serviceId2Name } from '../../store/by-reviewing-service'
import '@source-data/render-rev'

export default {
  props: {
    article: Object,
    expandedReview: Number,
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
  },
  mounted() {
    const md = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: true
    });
    const doi = this.article.doi;
    const el = this.$refs[doi];
    const display = {
      publisherName: name => {
        const nameMap = {
          'embo press': 'EMBO Press',
          'peer ref': 'Peer Ref',
          'review commons': 'Review Commons',
        };
        return nameMap[name] || name;
      },
      renderMarkdown: src => md.render(src),
    };
    el.configure({ doi, display });
  }
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
