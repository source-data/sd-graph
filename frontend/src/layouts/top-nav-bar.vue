<template lang="pug">
  v-app-bar(
    app
    height=90
    color="tertiary"
    hide-on-scroll
    scroll-threshold=0
    scroll-off-screen tile elevation=1
  )

    v-toolbar-title
      .text-md-h4.text-sm-h5.text-h5.pointer.banner-title
        a(:href="$router.resolve({name: 'Home'}).href") {{ $t('app.title') }}
      .text-md-h5.text-sm-h6.text-subtitle-2.pointer.banner-subtitle
        a(:href="$router.resolve({name: 'Home'}).href") {{ $t('app.subtitle') }}

    v-spacer

    a(href="https://embo.org" target="_blank")
      img(src="../assets/EMBO_logo.svg" :alt="$t('logo.alt.embo')" height="40rem").ml-2

    template(v-slot:extension)
      v-tabs(
        center-active
        show-arrows
        wrap
        row
        justify-end
      )
        v-tab(to="/refereed-preprints") {{ $t('article_list.title') }}
        v-spacer
        v-tab(to="/about") {{ $t('about.title') }}
        v-tab(to="/contact") {{ $t('contact.title') }}
</template>

<style lang="scss" scoped>
.banner-title {
  color:#0a5769;
}
.banner-subtitle {
  color:#217b90;
}
</style>