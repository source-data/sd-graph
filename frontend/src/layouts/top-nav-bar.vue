<template lang="pug">
    v-app-bar(
      app 
      clipped-left 
      prominent
      color="blue-grey darken-2"
      shrink-on-scroll
      fade-img-on-scroll
      scroll-threshold="700"
      src="../assets/EEB_HP_Banner.svg"
    )
    //-   a(href="https://embo.org" target="_blank" rel="noopener")
    //-     img(src="../assets/EEB_E_LOGO.png" class="banner-logo banner-logo--embo" alt="EMBO Logo")
    //- .org-credits--right
    //-   a(href="https://embopress.org")
    //-     img(src="../assets/EEB_EP_LOGO.png" class="banner-logo banner-logo--press" alt="EMBO Press Logo")
    //-   a(href="https://sourcedata.io" target="_blank" rel="noopener")
    //-     img(src="../assets/EEB_SD_LOGO.png" class="banner-logo banner-logo--sourcedata" alt="SourceData Logo")

</template>

<style lang="scss" scoped>
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
}
</style>