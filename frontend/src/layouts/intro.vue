<template lang="pug">
    div(class="px-5")
      p
        | <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b>
        |  that  combines artificial intelligence with human curation
        |  and expert peer-review to highlight results posted in
        |
        a(href="https://biorxiv.org" target="_blank" rel="noopener") bioRxiv
        |  preprints. EEB is a technology experiment developed by
        |
        a(href="https://embopress.org" target="_blank" rel="noopener") EMBO Press
        |
        | and
        |
        a(href="https://sourcedata.io" target="_blank" rel="noopener") SourceData
        |.
      p
        | Follow
        |
        a(href="https://twitter.com/EarlyEvidence" target="_blank" rel="noopener") @EarlyEvidence
        |  on Twitter to receive updates and new highlighted preprints.
      p 
        | Discover preprints with one of these methods:
        ul
            li
                //- i(class="el-icon-reading")
                b  Refereed Preprints:
                |  browse preprints that are linked to expert reviews.
            li
                //- i(class="fas el-icon-fa-flask")
                b  COVID-19 hypotheses:
                |  find recent studies related to the biology of SARS-CoV-2/COVID-19 based on hypotheses they are testing.
            li
                //- i(class="el-icon-magic-stick")
                b  Automagic:
                |  check out a selection of 20 SARS-CoV-2 preprints automatically highlighted based on their diversity in experimental approaches and biological topics.
            li
                //- i(class="el-icon-search")
                b  Search COVID-19 preprints:
                |  find preprints by keyword, author name or doi.

</template>
