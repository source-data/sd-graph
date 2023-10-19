<template lang="pug">
  v-app
    LeftSideBar
    TopNavBar
    v-main(style="padding-left:56px")
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

// /* Portrait */
// @media only screen
//   and (min-device-width: 375px)
//   and (max-device-width: 812px)
//   and (-webkit-min-device-pixel-ratio: 3)
//   and (orientation: portrait) {
//     .v-main.my-main {
//       padding: 0;
//     }
// }

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

</style>

