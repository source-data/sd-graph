<template lang="pug">
  div
    el-row(v-if="article")
      el-row()
        el-col(:span="24")
            h4 {{ article.title }} 
            small
              a(:href="full_url(article.doi)" target="_blank") {{ article.doi }}
            p
              small {{ authorList }}
      el-row()
        el-col(:span="10")
          small(style="line-height:1.5") {{ article.abstract }}
        el-col(:span="2")
          p
        el-col(:span="12")
          p 
            label(for="carousel") {{ panels.length }} panel(s) of interest:
          el-carousel(indicator-position="outside" arrow="hover" :autoplay="false" height="" id="carousel")
            el-carousel-item(v-for="panel in panels" :key="panel.id" style="text-align:left")
              el-card(class="box-card" shadow="always")
                small {{ panel.caption }}
            //- a(:href="panel.url")
            //-   el-image(:src="panel.img_url" fit="contain")
            //- p
            //-   a(:href="panel.url") Open in SmartFigure
    el-divider
</template>
<script>
export default {
  props: {
    article: Object,
  },
  methods: {
      full_url (doi) {
          return new URL(doi, "https://doi.org/")
      }
  },
  computed: {
    authorList () {
      return this.article.authors.map(author => `${author[0]} ${author[1]}`).join(', ')
    },
    panels () {
      return this.article.panels
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