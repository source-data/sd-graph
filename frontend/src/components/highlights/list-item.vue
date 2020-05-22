<template lang="pug">
  div
    el-row(v-if="article")
      el-row()
        el-col(:span="24")
            h4 {{ article.title}} 
            a(:href="article.doi") {{ article.doi }}
            small
            p {{ authorList }}
      el-row()
        el-col(:span="10")
          p {{ article.abstract }}
        el-col(:span="2")
          p
        el-col(:span="12")
          p 
            label(for="carousel") Panels of interest:
          el-carousel(indicator-position="outside" :autoplay="false" height="" style="border: solid 1px; border-color: #2222DD" id="carousel")
            el-carousel-item(v-for="panel in panels" :key="panel.id" style="text-align:left")
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