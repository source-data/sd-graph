<template lang='pug'>
v-container
    v-row(
        v-for='article in articles'
        :key='article.id'
    )
        v-col
            v-card(
                class='pa-5'
                color='blue-grey lighten-5'
            )
                v-card-title
                    | {{ article.title }}
                    router-link(:to='`/doi/${article.doi}`')
                        v-icon(color='indigo lighten-3') mdi-link-variant
                v-card-subtitle
                    v-container(fluid)
                        v-row
                            v-col
                                p {{ authorList(article) }}
                                p
                                    | Posted
                                    |
                                    b {{ displayDate(article.pub_date) }}
                                    |  on
                                    |
                                    i {{ article.journal }}
                                p
                                    b doi:
                                    a(:href='href(article.doi)' target='_blank' rel='noopener')
                                        |
                                        | {{ href(article.doi) }}
                            v-col
                                render-rev(:doi='article.doi' :ref='article.doi')
                v-card-text
                    v-card
                        v-card-title Abstract
                        v-card-text
                            p(class='text--primary') {{ article.abstract }}
</template>


<script>
import httpClient from '../lib/http';
import MarkdownIt from 'markdown-it';
import '@source-data/render-rev';

export default {
    name: 'RenderRevDemo',
    data() {
        return {
            articles: []
        }
    },
    methods: {
        authorList(article) {
            // first, clone the authors array because sort() operates in-place on the array it's called on.
            const authorsSortedByPosition = article.authors.slice(0);
            function byPosition(a, b) {
                return a['position_idx'] - b['position_idx']
            }
            authorsSortedByPosition.sort(byPosition);
            return authorsSortedByPosition.map(author => `${author.surname ? author.surname + ' ' : ''}${author.given_names ? author.given_names : ''}${author.collab ? author.collab : ''}${(author.corresp == 'yes' ? '*' : '')}`).join(', ')
        },
        displayDate(date_str) {
            // date_str needs to be in ISO 8601 format for Safari; YYYY-M-DD instead of YYYY-MM-DD will NOT work!
            const date = new Date(date_str)
            const year = date.getFullYear()
            const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
            const month = months[date.getMonth()]
            const day = date.getDate()
            return month + ' ' + day + ', ' + year
        },
        href(doi) {
            return new URL(doi, 'https://doi.org/').href
        }
    },
    created() {
        const dois = [
            '10.1101/2020.07.20.212886',
            // '10.1101/2022.03.25.485742',
            '10.1101/2022.02.24.481763',
            '10.1101/2021.10.26.465695',
            // '10.1101/2022.07.22.22277924',
        ];
        const self = this;
        httpClient
            .post('https://eeb.embo.org/api/v1/dois/', { dois: dois })
            .then(response => response.data)
            .then(articles => {
                self.articles = articles
            })
    },
    watch: {
        articles: function configureRenderRev(articles) {
            const self = this;
            this.$nextTick(function () {
                const md = new MarkdownIt({
                    html: true,
                    linkify: true,
                    typographer: true
                });
                articles.forEach(article => {
                    const doi = article.doi;
                    const el = self.$refs[doi][0];
                    const display = {
                        publisherName: name => {
                            const nameMap = {
                                'embo press': 'EMBO Press',
                                'peer ref': 'Peer Ref',
                                'review commons': 'Review Commons',
                            };
                            return nameMap[name] || name;
                        },
                        renderMarkdown: src => md.render(src),
                    };
                    el.configure({ doi, display });
                });
            });
        }
    }
}
</script>
