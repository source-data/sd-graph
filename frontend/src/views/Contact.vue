<template lang="pug">
  v-card(flat).col-lg-8.col-md-9.col-sm-10.col-xs-12.ml-auto.mr-auto
    v-card-title {{ $t('contact.title') }}
    v-card-text.text-body-1(v-html="$t('contact.text_html')")
</template>