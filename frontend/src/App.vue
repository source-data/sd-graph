<template lang="pug">
  el-container
    TopNavBar
    Banner
    el-container
      LeftSideBar
      el-main
        router-view
    el-footer
      Footer

</template>

<script>
import TopNavBar from './layouts/top-nav-bar'
import Banner from './layouts/banner'
import LeftSideBar from './layouts/left-side-bar'
import Footer from './layouts/footer'

export default {
  name: 'app',
  components: {
    TopNavBar,
    Banner,
    LeftSideBar,
    Footer,
  },
  metaInfo: {
    meta: [
      { name: 'description', content: 'Early Evidence Base (EEB) is an experimental platform that combines artificial intelligence with human curation and expert peer-review to highlight results posted in bioRxiv preprints developed by EMBO Press.' }
    ],
    title: 'Accessing early scientific findings',
    // all titles will be injected into this template
    titleTemplate: '%s | Early Evidence Base'
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

.margin-5 {
  margin: 5px;
}
.spaced-row {
  padding: 1px;
}

.pointer {
  cursor: pointer;
}

</style>


