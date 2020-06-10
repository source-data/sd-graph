<template lang="pug">
  div
    el-row(v-if="article")
      el-row()
        el-col(:span="24")
            h3 {{ article.title }} 
            //- el-row(type="flex" justify="space-between")
            p
              small() Posted 
                b {{ displayDate(article.pub_date) }}
                |  on 
                i {{ displayJournal(article.journal) }}
            p
              small
                b  doi:  
                el-link(type="primary" :href="href(article.doi)" target="_blank") http://doi.org/{{ article.doi }} 
            p
              small {{ authorList }}
            div(v-if="article.review_process")
              el-collapse(v-for="review in article.review_process.reviews" accordion)
                el-popover(v-if="review.highlight",
                    placement="top",
                    title="Summary (click tab for full review)",
                    width="600",
                    trigger="hover",
                    :content="review.highlight",
                    transition="el-fade-in-linear",
                    :visible-arrow="false",
                    :open-delay="500"
                  )
                  //-  div(v-html="mdRender(review.highlight)")
                  el-collapse-item(slot="reference")
                    p(slot="title")
                      span.peer_review_material Reviewed by 
                        i {{ displayJournal(review.reviewed_by) }}
                      |  | Reviewer #
                      | {{ review.review_idx }}
                    p(v-html="mdRender(review.text)")
              el-collapse(v-if="article.review_process.response")
                el-collapse-item
                  p(slot="title")
                    span.peer_review_material Response to the Reviewers
                  p(v-html="mdRender(article.review_process.response.text)")
              el-collapse(v-if="article.review_process.annot")
                el-collapse-item(:title="'Reviewed by ' +  + ' | Review Process File'")
                  p(slot="title")
                    span.peer_review_material Reviewed by 
                      i {{ displayJournal(article.review_process.annot.reviewed_by) }}
                    |  | Review Process File
                  p(v-html="mdRender(article.review_process.annot.text)")
      el-row()
        el-col(:span="10")
          p
            small(style="line-height:1.5") {{ article.abstract }}
          p 
            small(style="font-family: monospace; font-size: 9px") [source: {{ article.source }}]
        el-col(:span="2")
          p
        el-col(:span="12")
          //- label(for="info-cards" style="font-variant: small-caps") {{ info.length }} information card{{ info.length > 1 ? 's':''}}:
          el-collapse(v-for="(card, index) in info" id="infor-cards" v-model="activeCards")
            el-collapse-item(:title="card.title", :name="index")
              div(v-if="card.text instanceof Array")
                span(v-for="item in card.text")
                   el-tag(size="medium") {{ item }}
              div(v-if="typeof card.text === 'string'")
                small {{ card.text }}
    el-divider
</template>
<script>

import MarkdownIt from 'markdown-it'

import { mapGetters} from 'vuex'

export default {
  props: {
    article: Object,
  },
  data() {
    return {
      activeCards: [0]
    }
  },
  methods: {
    href(doi) {
        return new URL(doi, "https://doi.org/").href
    },
    displayDate(date_str) {
        const date = new Date(date_str)
        const year = date.getFullYear()
        const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
        const month = months[date.getMonth()]
        const day = date.getDate()
        return month + ' ' + day + ', ' + year 
    },
    mdRender (md_text) {
      const md = new MarkdownIt({
          html: true,
          linkify: true,
          typographer: true
      })
      return md.render(md_text)
    },
    displayJournal(id) {
      return this.journalName(id)
    }
  },
  computed: {
    ...mapGetters(['journalName']),
    authorList () {
      return this.article.authors.map(author => `${author.surname} ${author.given_names}${(author.corresp=='yes'?'*':'')}`).join(', ')
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
  .peer_review_material {
    color:#364497;
    font-weight: bold;
  }
</style>
