import Vue from 'vue'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)

export default new VueI18n({
  locale: 'en',
  messages: {
    en: {
      // the key format is "page.section.key", e.g. "home.title" will be used for the title of the home page

      /*
       * website banner
       */
      'app.title': 'Early Evidence Base',
      'app.subtitle': 'Collecting and Assessing Reviewed Preprints',
      'app.credits_prefix': 'an initiative by',

      /*
       * the meta keys are used for the meta tags in the head section of the page
       */
      'meta.description': 'Early Evidence Base (EEB) is an experimental platform that combines artificial intelligence with human curation and expert peer-review to highlight results posted in bioRxiv preprints developed by EMBO Press.',
      // the title of the page will be "Accessing early scientific findings | Early Evidence Base"
      'meta.title': 'Accessing early scientific findings',
      'meta.titleTemplate': '{titleChunk} | Early Evidence Base',

      /*
       * about page
       */
      'about.title': 'About EEB',
      'about.text_html': `
        <p>
          <i>Early Evidence Base</i> (EEB) is an <b>experimental platform</b> that combines artificial intelligence with human curation and expert peer-review to highlight results posted in preprints. EEB is a technology experiment developed by <a href="https://embopress.org" target="_blank" rel="noopener">EMBO Press</a> and <a href="https://sourcedata.io" target="_blank" rel="noopener">SourceData</a>.
        <p>
          Preprints provide the scientific community with early access to scientific evidence. For experts, this communication channel is an efficient way to accesss research without delay and thus to accelerate scientific progress. But for non-experts, navigating preprints can be challenging: in absence of peer-review and journal certification, interpreting the data and evaluating the strength of the conclusions is often impossible; finding specific and relevant information in the rapidly accumulating corpus of preprints is becoming increasingly difficult.
        <p>
          The COVID-19 pandemic has made this tradeoff even more visible. The urgency in understanding and combatting SARS-CoV-2 viral infection has stimulated an unprecedented rate of preprint posting. It has however also revealed the risk resulting from misinterpretation of preliminary results shared in preprint and with amplification or perpetuating prelimature claims by non-experts or the media.
        <p>
          To experiment with ways in which technology and human expertise can be combined to address these issues, EMBO has built the EEB. The platform prioritizes preprints in complementary ways:
          <ul>
            <li>
              Refereed Preprints are preprints that are associated with reviews. EEB prioritizes such preprints and integrates the content of the reviews as well as the authors' response, when available, to provide rich context and in-depth analyses of the reported research.
            </li>
            <li>
              To highlight the importance of experimental evidence, EEB automatically highlights and organizes preprints around scientific topics and emergent areas of research.
            </li>
            <li>
              Finally, EEB provides an automated selection of preprints that are enriched in studies that were peer reviewed, may bridge several areas of research and use a diversity of experimental approaches.
            </li>
          </ul>`,

      /*
       * contact page
       */
      'contact.title': 'Contact',
      'contact.text_html': `
        <p>
          EEB is under development and is run as an experiment to push boundaries in transparency and scientific publishing. Please send us your thoughts, suggestions and feedback to: <a href="mailto:thomas.lemberger@embo.org" type="primary">thomas.lemberger@embo.org</a>`,

      /*
       * not found page
       */
      'not_found.title': "Oops, you've encountered an error 404",
      'not_found.message': "It appears the page you were looking for doesn't exist. Sorry about that.",

      /*
       * filters component
       */
      'filters.published_in.title': 'Filter by journal',
      'filters.published_in.subtitle': 'Filter the reviewed preprints by the journal they were published in',
      'filters.published_in.label': 'Select publishers',
      'filters.reviewed_by.title': 'Filter by reviewer',
      'filters.reviewed_by.subtitle': 'Filter the reviewed preprints by the reviewer',
      'filters.search.title': 'Filter by terms',
      'filters.search.subtitle': 'Filter the reviewed preprints by terms such as keywords in titles, author, doi, etc.',
      'filters.search.placeholder': 'keywords, authors, doi',
      'filters.search.clear': 'Clear search',

      /*
       * review service summary component
       */
      'review_service_summary.title_html': 'About <a href="{url}" target="_blank" rel="noopener">{name}</a>',
      'review_service_summary.process.title': 'Process',
      'review_service_summary.process.submit.author_driven': 'Author-driven',
      'review_service_summary.process.submit.author_independent': 'Author-independent',
      'review_service_summary.process.submit.tooltip.question': 'Who submitted the manuscript or initiated the feedback process?',
      'review_service_summary.process.submit.tooltip.answer': '{review_requested_by}.',
      'review_service_summary.process.reviewer_selection.service': 'Service-selected reviewers',
      'review_service_summary.process.reviewer_selection.self': 'Self-nominated reviewers',
      'review_service_summary.process.reviewer_selection.author': 'Author-selected reviewers',
      'review_service_summary.process.reviewer_selection.tooltip.question': 'Who selects the reviewers?',
      'review_service_summary.process.reviewer_selection.tooltip.answer': '{reviewer_selected_by} select the reviewers.',
      'review_service_summary.process.public_interaction.yes': 'Public feedback',
      'review_service_summary.process.public_interaction.no': 'No public interactions',
      'review_service_summary.process.public_interaction.tooltip.question': 'Was there an opportunity for the public to engage as an integral part of the process?',
      'review_service_summary.process.public_interaction.tooltip.answer': '{public_interaction}.',
      'review_service_summary.process.author_response.yes': 'Authors reply',
      'review_service_summary.process.author_response.no': 'No author reply',
      'review_service_summary.process.author_response.tooltip.question': 'Was the author’s response included as an integral part of the process?',
      'review_service_summary.process.author_response.tooltip.answer': '{opportunity_for_author_response}.',
      'review_service_summary.process.recommendation.binary': 'Binary decision',
      'review_service_summary.process.recommendation.scale': 'Scaled rating',
      'review_service_summary.process.recommendation.no': 'No decision',
      'review_service_summary.process.recommendation.tooltip.question': 'Does the service provide a decision/recommendation or a scalar rating after the review process?',
      'review_service_summary.process.recommendation.tooltip.answer': 'Recommendation provided: {recommendation}.',
      'review_service_summary.policy.title': 'Policy',
      'review_service_summary.policy.guidelines.title': 'Review guidelines:',
      'review_service_summary.policy.guidelines.description_html': 'Yes (<a href="{url}" target="_blank" rel="noopener">read more</a>)',
      'review_service_summary.policy.guidelines.tooltip': 'Explicit guidelines for reviewers',
      'review_service_summary.policy.coverage.title': 'Review coverage:',
      'review_service_summary.policy.coverage.description': '{review_coverage}',
      'review_service_summary.policy.coverage.tooltip': 'Does the feedback cover the entire paper or only a certain section or aspect?',
      'review_service_summary.policy.identity.title': 'Reviewer identity known to:',
      'review_service_summary.policy.identity.description': '{reviewer_identity_known_to}',
      'review_service_summary.policy.identity.tooltip': 'Are the identities of reviewers known to everyone (public), editors or service, or no one?',
      'review_service_summary.policy.competing_interests.title': 'Competing interests:',
      'review_service_summary.policy.competing_interests.description': '{competing_interests}',
      'review_service_summary.policy.competing_interests.tooltip': 'Is a declaration of competing interest required?',

      /*
       * single-article sub-page
       */
      'single_article.not_found.slug': "The requested article was not found.",
      'single_article.not_found.doi_html': "The article with DOI: <code>{doi}</code> was not found.",

      /*
       * article list sub-page
       */
      'article_list.title': 'Browse',
      'article_list.gt_0.title': '{n} reviewed preprints found',
      'article_list.eq_0.title': "Sorry, we couldn't find any results",
      'article_list.eq_0.subtitle': 'Try changing some of the filter values.',
      'article_list.sort.by.preprint_date.label': 'preprint date',
      'article_list.sort.by.preprint_date.tooltip': 'Sort by preprint date',
      'article_list.sort.by.reviewing_date.label': 'reviewing date',
      'article_list.sort.by.reviewing_date.tooltip': 'Sort by reviewing date',
      'article_list.sort.order.asc.label': 'ascending',
      'article_list.sort.order.asc.tooltip': 'Show earliest first',
      'article_list.sort.order.desc.label': 'descending',
      'article_list.sort.order.desc.tooltip': 'Show latest first',
      'article_list.collapse_abstracts': 'Collapse all abstracts',

      /*
      * article component
      */
      'article.actions.copy.link': 'Copy link to clipboard',
      'article.actions.copy.citation': 'Copy citation',
      'article.actions.share.x': 'Share on X',
      'article.info.posted_on': 'Posted <b>{date}</b> on <i>{server}</i> <a href="{url}" target="_blank" rel="noopener" class="ml-2">doi.org/{doi}</a>',
      'article.abstract.title': 'Abstract',
      'article.figure_keywords.title': 'Preprint figure keywords',
      'article.figure_keywords.info.title': 'Keywords deduced from the figures.',
      'article.figure_keywords.info.message': 'Green text means this, orange text means that...',
      'article.reviews.title': 'Preprint review timeline',
      'article.reviews.peer_reviewed_by': 'Reviewed by',
      'article.reviews.summary.title': 'Automated summary of preprint reviews',
      'article.reviews.summary.info.message': 'This summary was generated automatically using ChatGPT-4 based on the content of the reviews. Currently, this feature is limited to Review Commons reviews. To access the full content of the original reviews, click on "Peer Review".',
      'article.cite.title': 'Cite reviewed preprint',
      'article.cite.btn.tooltip': 'Click to copy reviewed preprint citation',
      'article.cite.text.reviewed_by': 'peer reviewed by <b><i>{service}</i></b>',
      'article.cite.text.citation': '{authors} ({year}). {title}. <b><i>{journal}</i></b> doi.org/{doi}, {reviewedBy} {reviewedPreprintUrl}.',

      /*
       * logo alt texts
       */
      'logo.alt.embo': 'EMBO Logo',
      'logo.alt.embo_press': 'EMBO Press Logo',
      'logo.alt.sourcedata': 'SourceData Logo',
      'logo.alt.github': 'GitHub Logo',

      /*
       * snackbar messages
       */
      'snack.message.copied': 'Text copied to clipboard!',
      'snack.message.error.server': 'An unexpected server error occured. Please try again in a moment...',
      'snack.message.error.request': 'There was an error with your request. Please check your request and try again in a moment...',
    },
  }
})
