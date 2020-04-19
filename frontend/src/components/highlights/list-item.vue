<template lang="pug">
    div
        el-row(v-if="article")
            el-col(:span="12")
                h4 {{ article.title}}
                small
                    em(v-for="author in article.authors") {{ author }},
                br
                small
                    a(:href="article.doi") {{ article.doi }}
                p {{ article.abstract }}
            el-col(:span="12")
                el-carousel(indicator-position="outside" autoplay="false" height="")
                    el-carousel-item(v-for="panel in article.smart_figure" :key="panel.url" style="text-align:center")
                        a(:href="panel.url")
                            el-image(:src="panel.img_url" fit="contain")
                        p
                            a(:href="panel.url") Open in SmartFigure
        el-divider
</template>
<script>
export default {
    props: {
        article: Object,
    },
}
</script>