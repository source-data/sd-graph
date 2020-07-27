<template lang="pug">
  el-container
    .org-credits
      .org-credits--left
        a(href="https://embo.org" target="_blank")
          img(src="./assets/EEB_E_LOGO.png" class="banner-logo banner-logo--embo" alt="EMBO Logo")
      .org-credits--right
        a(href="https://embopress.org")
          img(src="./assets/EEB_EP_LOGO.png" class="banner-logo banner-logo--press" alt="EMBO Press Logo")
        a(href="https://sourcedata.io" target="_blank")
          img(src="./assets/EEB_SD_LOGO.png" class="banner-logo banner-logo--sourcedata" alt="SourceData Logo")
    header.banner-area
      img(src="./assets/EEB_HP_Banner.svg").banner-image
      .banner-title-wrapper
        router-link(to="/"  active-class="is-active")
          h1.title.pointer.banner-title Early Evidence Base
        h3.banner-subtitle Accessing early scientific findings
    el-container
      el-aside(width="180px" style="border-right-style: solid; border-right-width: 1px; padding-top: 50px")
        el-menu(default-active="1")
          router-link(to="/"  active-class="is-active")
            el-menu-item(index="0")
              span.el-icon-s-home
              | Home
          router-link(to="/about"  active-class="is-active")
            el-menu-item(index="1") About
          el-menu-item(index="2" disabled) For developers
          el-menu-item(index="3" disabled) Contact
        el-divider
        div(style="padding:10px")
          small Database stats:
            p
              code {{ db_stats.ai_annotated || 0 }}
              |  preprints automatically annotated.
            p
              code {{ db_stats.sd_annotated || 0 }}
              |  experiments in the SourceData knowledge graph
            p
              code {{db_stats.total_nodes || 0 }}
              |  nodes in EEB.
      el-main
        router-view
    el-footer
      el-row
        el-col(:span="16" :offset="4")
          small EMBO 	&#169; {{ thisYear }}

</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'app',
  metaInfo: {
    meta: [
      { name: 'description', content: 'Early Evidence Base (EEB) is an experimental platform that combines artificial intelligence with human curation and expert peer-review to highlight results posted in bioRxiv preprints developed by EMBO Press.' }
    ]
  },
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
    ...mapGetters(['db_stats'])
  },
  beforeCreate () {
    this.$store.dispatch('statsFromFlask').then(
      () => this.$store.commit('incrementInit')
    )
    this.$store.dispatch('byReviewingService/getAll').then(
      () => {
        this.$store.dispatch('highlights/listByCurrent', 'byReviewingService').then(
          () => {
            this.$store.commit('highlights/sortRecords', {
              sortBy: 'posting_date',
              direction: 'desc',
            })
          }
        )
      }
    ).then(
          () => this.$store.commit('incrementInit')
    ),
    this.$store.dispatch('byHyp/getAll').then(
      () => this.$store.commit('incrementInit')
    ),
    this.$store.dispatch('byAutomagic/getAll').then(
      () => this.$store.commit('incrementInit')
    ),
    this.$store.commit('highlights/updateSelectedTab', 'byReviewingService')
  },
}
</script>

<style lang="scss">
html, body {
  padding:0;
  margin:0;
}

a {
  text-decoration: none;
  color: #66b1ff;
}

.el-menu-item a {
  color: inherit;
}

.md-content {
  max-height:350px;
  overflow: scroll;
}
.md-content img {
  max-height: 60px;
}

.margin-0 {
  margin: 0;
}
</style>

<style scoped lang="scss">
#header {
  border-bottom-style: solid;
  border-bottom-width: 1px;
}

.banner-image {
  display:none;
}

@media screen and (min-width:680px) {
  .banner-image {
    display:block;
    width:100%;
  }
}

.banner-area {
  position:relative;
  display:block;
  background-image: url("./assets/EEB_HP_Banner.svg");
  background-size:cover;
}

@media screen and (min-width:680px) {
  .banner-area {
    position:relative;
    display:flex;
    align-items:center;
    background-image:none;
  }
}


.banner-title-wrapper {
  padding: 2rem 2rem;
  background-color: rgba(255,255,255,0.75);
}

@media screen and (min-width:680px) {
  .banner-title-wrapper {
    position: absolute;
    // top:2rem;
    left:180px;
    padding: 2rem 2rem;
    background-color: rgba(255,255,255,0.75);
  }
}

@media screen and (min-width:1080px) {
  .banner-title-wrapper {
      left: 180px;
  }
}

@media screen and (min-width:1160px) {
  .banner-title-wrapper {
    padding: 4rem 2rem;
  }
}

@media screen and (min-width:1800px) {
  .banner-title-wrapper {
    padding: 6rem 3rem;
  }
}

.banner-title {
  color:#0a5769;
  font-size: 2.5rem;
  line-height:1;

  margin:0 0 1rem 0;
}

.banner-subtitle {
  color:#217b90;
  font-size: 1.5rem;
  line-height:1;

  margin:0 0 0 0;
}

@media screen and (min-width:1080px) {
  .banner-title {
    font-size: 5rem;

  }

  .banner-subtitle {
    font-size: 2rem;

  }
}

@media screen and (min-width:1690px) {
  .banner-title {
    font-size: 6rem;
  }

  .banner-subtitle {
    font-size:3rem;
  }
}


.org-credits {
  display:flex;
  justify-content: space-between;
  padding: 1rem;
  background: #f5f5f5
}

.org-credits--left, .org-credits--right {
  display:flex;
  align-items: center;
}

.org-credits--right .banner-logo {
  margin-left:2rem;
}


.org-credits--right {
  flex-direction:column;
  justify-content: center;
}
.banner-logo--press,
.banner-logo--sourcedata {
  max-height:30px
}


@media screen and (min-width:680px) {

.org-credits--right {
  flex-direction:row;
  justify-content: flex-end;
}
.banner-logo--press,
.banner-logo--sourcedata {
  max-height:none;
}

}


// .title {
//   font-size: 36px;
//   font-style: normal !important;
//   font-family: 'Open Sans', Arial, sans-serif;
// }

.banner_img {
  background-image: url("./assets/EEB_HP_Banner.svg");
  background-size:cover;
}

.pointer {
   cursor: pointer;
}

img.center-img {
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.vertical-align {
  margin-top: 80px;
  transform: translate(0, -50%)
}

.side_bar_links {
  padding-left: 25px;
}


</style>


