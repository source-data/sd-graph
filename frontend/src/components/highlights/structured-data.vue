<template>
  <script v-html="jsonld", type="application/ld+json">
</template>

<script>
export default {
  props: {
    article: Object,
  },
  data () {
    const jsonld = {
        "@context": "http://schema.org/",
        
        "@type": "Dataset",
        "@id": "https://search.sourcedata.io/panel/29378",
        "dateModified": "2015-03-26",
        "dateCreated": "2015-03-26",
        "name": "c-Jun activity up-regulation by RAF inhibitors causes resistance to apoptosis: Figure 3-E",
        "description": "E, F Apoptosis in WM115 cells with or without 48 h JUN knockdown after 96-h treatment with increasing doses of vemurafenib. List of tagged entities: WM115 (cellosaurus:CVCL_0040), vemurafenib (CHEBI:63637), JUN (ncbigene:3725), fluorescence microscopy (bao:BAO_0000450)",
        "url": "https://search.sourcedata.io/panel/29378",
        "includedInDataCatalog": {
            "@type": "DataCatalog",
            "name": "SourceData",
            "url": "https://search.sourcedata.io"
        },
        "citation": {
            "@type": "ScholarlyArticle",
            "text": "Peter, K Sorger, Mohammad Fallahi-Sichani, Nathan Moerke, Mario Niepel, Tinghu Zhang, Nathanael, Schiander Gray (2015), Systematic analysis of BRAF(V600E) melanomas reveals a role for JNK/c-Jun pathway in adaptive resistance to drug-induced apoptosis., Molecular systems biology, doi:10.15252/msb.20145877",
            "headline": "Figure 3-E - Systematic analysis of BRAF(V600E) melanomas reveals a role for JNK/c-Jun pathway in adaptive resistance to drug-induced apoptosis.",
            "datePublished": "2015-03-26",
            "url": "https://www.doi.org/10.15252/msb.20145877",
            "image": "https://search.sourcedata.io/php/api//file.php?panel_id=29378"
        },
        "author": [
            {
            "@type": "Person",
            "name": "Peter, K Sorger",
            "worksFor": {
                "@type": "Organization",
                "name": "Harvard Medical School, 200 Longwood Ave., Boston, MA, 02115, United States [US]"
            }
            },
            {
            "@type": "Person",
            "name": "Mohammad Fallahi-Sichani",
            "worksFor": {
                "@type": "Organization",
                "name": "Unknown, 200 Longwood Ave., Boston, MA, 02115, United States [US]"
            }
            },
            {
            "@type": "Person",
            "name": "Nathan Moerke",
            "worksFor": {
                "@type": "Organization",
                "name": "Harvard Medical School, 200 Longwood Ave., Boston, MA, 02115, United States [US]"
            }
            },
            {
            "@type": "Person",
            "name": "Mario Niepel",
            "worksFor": {
                "@type": "Organization",
                "name": "Harvard Medical School, 200 Longwood Ave, Boston, MA, 02115, United States [US]"
            }
            },
            {
            "@type": "Person",
            "name": "Tinghu Zhang",
            "worksFor": {
                "@type": "Organization",
                "name": "Harvard Medical School, 250 Longwood Ave., Boston, 02115"
            }
            },
            {
            "@type": "Person",
            "name": "Nathanael, Schiander Gray",
            "worksFor": {
                "@type": "Organization",
                "name": "Harvard Medical School, Biological Chemistry and Molecular Pharmacology, 250 Longwood Ave, Boston, MA, 02115, United States [US]"
            }
            }
        ],
        "keywords": "WM115 (cellosaurus:CVCL_0040), vemurafenib (CHEBI:63637), JUN (ncbigene:3725), fluorescence microscopy (bao:BAO_0000450)",
        "variableMeasured": [
            {
            "@type": "PropertyValue",
            "name": "WM115",
            "sameAs": "https://identifiers.org/cellosaurus:CVCL_0040",
            "propertyID": "cellosaurus:CVCL_0040",
            "measurementTechnique": [
                "fluorescence microscopy"
            ]
            }
        ],
        "distribution": {
            "@type": "DataDownload",
            "contentUrl": "http://myDownloadLink.com",
            "fileFormat": "application/zip",
            "dateCreated": "2020-04-29 11:19:27",
            "dateModified": "2020-04-29 11:19:27",
            "datePublished": "2020-04-29 11:19:27",
            "license": "https://creativecommons.org/licenses/by/2.0/legalcode"
        }
    }
    return {
      jsonld
    }
  }
}
</script>