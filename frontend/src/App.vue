<template lang="pug">
  v-app
    LeftSideBar
    TopNavBar
    v-main(style="padding-left:56px")
      v-container(fluid).main-content
        router-view
    v-footer
      Footer
</template>

<script>
import TopNavBar from './layouts/top-nav-bar'
import Banner from './layouts/banner'
import LeftSideBar from './layouts/left-side-bar'
import Footer from './layouts/footer'

export default {
  name: 'App',

  components: {
    TopNavBar,
    Banner,
    LeftSideBar,
    Footer
  },
  metaInfo: {
    meta: [
      {
        vmid: 'description',
        name: 'description',
        content: 'Early Evidence Base (EEB) is an experimental platform that combines artificial intelligence with human curation and expert peer-review to highlight results posted in bioRxiv preprints developed by EMBO Press.',
      }
    ],
    title: 'Accessing early scientific findings',
    // all titles will be injected into this template
    titleTemplate: '%s | Early Evidence Base'
  },
  data: () => ({
    //
  }),
};
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

.pointer {
  cursor: pointer;
}

// make the main container fluid up to a certain size
.container.container--fluid.main-content {
  max-width: 1200px;
  padding: 0;
}
</style>
