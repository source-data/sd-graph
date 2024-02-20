<template lang="pug">
  v-footer(padless).d-flex.flex-grow-1
    router-link(to="/about")
      v-list-item(index="1")
        span {{ $t('about.title') }}
    router-link(to="/contact")
      v-list-item(index="2")
        span {{ $t('contact.title') }}
    a(href="https://github.com/source-data/sd-graph" target="_blank" rel="noopener")
      v-list-item(index="3")
        span {{ $t('for_devs.title') }}

    v-spacer

    span EMBO &#169; {{ thisYear }}
</template>

<script>
export default {
  name: 'Footer',
  computed: {
    thisYear () {
      return new Date().getFullYear()
    },
  },
}
</script>

<style>
.gh-badge {
  width:35px;
}
</style>