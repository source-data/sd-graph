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
                el-link(type="primary", :href="href(article.doi)", target="_blank") http://doi.org/{{ article.doi }} 
            p
              small {{ authorList }}
            div(v-if="article.review_process")
              el-collapse(v-for="review in article.review_process.reviews" v-model="activeCollapseItem" accordion)
                el-collapse-item
                  p(slot="title")
                      el-popover(v-if="review.highlight" 
                        placement="top"
                        title="Summary (click tab to read the full review)"
                        width="600"
                        trigger="hover"
                        :content="review.highlight"
                        transition="el-fade-in-linear"
                        :visible-arrow="false"
                        :open-delay="500"
                      )
                        span(slot="reference").peer_review_material
                          i.el-icon-document-checked
                          |   Reviewed by 
                          i {{ displayJournal(review.reviewed_by) }}
                          |  | Reviewer #
                          | {{ review.review_idx }}
                      span(v-else).peer_review_material
                        i.el-icon-document-checked
                        |   Reviewed by 
                        i {{ displayJournal(review.reviewed_by) }}
                        |  | Reviewer #
                        | {{ review.review_idx }}
                  p(v-html="mdRender(review.text)" style="max-height:350px; overflow: scroll")
              el-collapse(v-if="article.review_process.response")
                el-collapse-item
                  p(slot="title")
                    span.peer_review_material
                      i.el-icon-notebook-2
                      |   Response to the Reviewers
                  p(v-html="mdRender(article.review_process.response.text)")
              el-collapse(v-if="article.review_process.annot")
                el-collapse-item(:title="'Reviewed by ' +  + ' | Review Process File'")
                  p(slot="title")
                    span.peer_review_material
                      i.el-icon-document-checked
                      |  Reviewed by 
                      i {{ displayJournal(article.review_process.annot.reviewed_by) }}
                    |  | Review Process File
                  p(v-html="mdRender(article.review_process.annot.text)")
      el-row(type="flex" justify="space-between")
        el-col(:span="11")
          p
            small(style="line-height:1.5") {{ article.abstract }}
          p 
            small(style="font-family: monospace; font-size: 9px") [source: {{ article.source }}]
        //- el-col(:span="2")
        //-   p
        el-col(:span="12")
          //- label(for="info-cards" style="font-variant: small-caps") {{ info.length }} information card{{ info.length > 1 ? 's':''}}:
          el-collapse(v-for="(card, index) in info" id="infor-cards" v-model="activeCards")
            el-collapse-item(:title="card.title", :name="index")
              div(v-if="card.entities.length > 1" )
                span(v-for="entity in card.entities")
                  el-tag(size="medium" :type="mapRole(entity.role)") {{ entity.text }}
              div(v-else-if="card.text instanceof Array")
                span(v-for="item in card.text")
                   el-tag(size="medium") {{ item }}
              div(v-else="typeof card.text === 'string'")
                small(style="line-height:1.3") {{ card.text }}
    el-divider
</template>
<script>

import MarkdownIt from 'markdown-it'

import { mapGetters } from 'vuex'

export default {
  props: {
    article: Object,
  },
  data() {
    return {
      activeCards: [0,1],
      activeCollapseItem: []
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
    displayJournal(id) {
      return this.journalName(id)
    },
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
