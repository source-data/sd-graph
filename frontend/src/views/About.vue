<template lang="pug">
  v-card(flat).col-lg-8.col-md-9.col-sm-10.col-xs-12.ml-auto.mr-auto
    span.d-flex.flex-row.align-center.mt-3
      a(href="https://embo.org" target="_blank" rel="noopener").pr-2.ml-auto
        img(src="../assets/EMBO_logo.svg" alt="EMBO Logo").logo-EMBO
      a(href="https://embopress.org" target="_blank" rel="noopener").pr-2
        img(src="../assets/EEB_EP_LOGO.png" alt="EMBO Press Logo").logo-EP
      a(href="https://sourcedata.io" target="_blank" rel="noopener").pb-1.mr-auto
        img(src="../assets/EEB_SD_LOGO.png" alt="SourceData Logo").logo-SD

    v-card-title About EEB
    v-card-text.text-body-1
      p <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
        |  that  combines artificial intelligence with human curation
        |  and expert peer-review to highlight results posted in
        |  preprints. EEB is a technology experiment developed by
        |
        a(href="https://embopress.org" target="_blank" rel="noopener") EMBO Press
        |
        | and
        |
        a(href="https://sourcedata.io" target="_blank" rel="noopener") SourceData
        |.

      p Preprints provide the scientific community with early access to scientific evidence.
        |
        | For experts, this communication channel is an efficient way to accesss research without delay and thus to accelerate scientific progress. But for non-experts, navigating preprints can be challenging: in absence of peer-review and journal certification, interpreting the data and evaluating the strength of the conclusions is often impossible; finding specific and relevant information in the rapidly accumulating corpus of preprints is becoming increasingly difficult.

      p The COVID-19 pandemic has made this tradeoff even more visible.
        |
        | The urgency in understanding and combatting SARS-CoV-2 viral infection has stimulated an unprecedented rate of preprint posting.
        | It has however also revealed the risk resulting from misinterpretation of preliminary results shared in preprint and with amplification or perpetuating prelimature claims by non-experts or the media.

      p To experiment with ways in which technology and human expertise can be combined to address these issues, EMBO has built the EEB.
        |
        | The platform prioritizes preprints in complementary ways: <!-- TODO: change wording here, to better reflect the current goals -->
        ul
          li Refereed Preprints are preprints that are associated with reviews. EEB prioritizes such preprints and integrates the content of the reviews as well as the authors' response, when available, to provide rich context and in-depth analyses of the reported research.
          li To highlight the importance of experimental evidence, EEB automatically highlights and organizes preprints around scientific topics and emergent areas of research.
          li Finally, EEB provides an automated selection of preprints that are enriched in studies that were peer reviewed, may bridge several areas of research and use a diversity of experimental approaches.
</template>

<style lang="scss" scoped>
.logo-EP {
  height: 30px;
}

.logo-EMBO {
  height: 30px;
}

.logo-SD {
  height: 15px;
}

@media only screen and (max-width: 600px) {
  .logo-EP {
    height: 22px;
  }
  .logo-EMBO {
    height: 22px;
  }
  .logo-SD {
    height: 13px;
  }
}

</style>