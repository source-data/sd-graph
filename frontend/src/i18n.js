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
      'app.subtitle': 'Discover and Cite Reviewed Preprints',

      /*
       * the meta keys are used for the meta tags in the head section of the page
       */
      'meta.description': 'Early Evidence Base aggregates reviewed preprints across several platforms and makes them citable.',
      // the title of the page will be "Accessing early scientific findings | Early Evidence Base"
      'meta.title': 'Latest Reviewed Preprints',
      'meta.titleTemplate': '{titleChunk} | Early Evidence Base',

      /*
       * about page
       */
      'about.title': 'About',
      'about.heading': 'About Early Evidence Base',
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
      'contact.heading': 'Contact',
      'contact.text_html': `
        <p>
          EEB is under development and is run as an experiment to push boundaries in transparency and scientific publishing. Please send us your thoughts, suggestions and feedback to: <a href="mailto:thomas.lemberger@embo.org" type="primary">thomas.lemberger@embo.org</a>`,

      /*
       * for developers
       */
      'for_devs.title': 'For developers',
      // just a link to the GitHub repo

      /*
       * not found page
       */
      'not_found.title': "Page not found",
      'not_found.message': "It appears the page you were looking for doesn't exist. Sorry about that.",

      /*
       * filters component
       */
      'filters.published_in.title': 'Filter by journal',
      'filters.published_in.subtitle': 'Select reviewed preprints published in specific journals',
      'filters.published_in.label': 'Select one or several journals',
      'filters.reviewed_by.title': 'Filter by reviewing platforms',
      'filters.reviewed_by.subtitle': 'Filter preprints reviewed by the selected peer review platforms',
      'filters.search.title': 'Search',
      'filters.search.subtitle': 'Search for keywords, authors, DOIs, ...',
      'filters.search.placeholder': 'keywords, authors, doi',
      'filters.search.clear': 'Clear search',
      'filters.search.errorMessages.minLength': 'Please enter at least {min} characters.',

      /*
       * review service summary component
       */
      'review_service_summary.title_html': 'About <a href="{url}" target="_blank" rel="noopener">{name}</a>',
      'review_service_summary.process.title': 'Peer review process',
      'review_service_summary.process.submit.author_driven': 'Author-driven submission',
      'review_service_summary.process.submit.author_independent': 'Author-independent',
      'review_service_summary.process.submit.tooltip.question': 'Who submitted the manuscript or inititated the request for peer review?',
      'review_service_summary.process.submit.tooltip.answer.author_driven': 'Authors.',
      'review_service_summary.process.submit.tooltip.answer.author_independent': 'Platform.',
      'review_service_summary.process.reviewer_selection.service': 'Platform-selected reviewers',
      'review_service_summary.process.reviewer_selection.self': 'Reviewers appointed themselves',
      'review_service_summary.process.reviewer_selection.author': 'Author-selected reviewers',
      'review_service_summary.process.reviewer_selection.tooltip.question': 'Who selects and invites the reviewers?',
      'review_service_summary.process.reviewer_selection.tooltip.answer.service': 'Editors or service select and invite reviewers.',
      'review_service_summary.process.reviewer_selection.tooltip.answer.self': 'Reviewers volunteer and appoint themselves.',
      'review_service_summary.process.reviewer_selection.tooltip.answer.author': 'Authors provide list of reviewers.',
      'review_service_summary.process.author_response.yes': 'Authors reply',
      'review_service_summary.process.author_response.no': 'No author reply',
      'review_service_summary.process.author_response.tooltip.question': 'Was the author’s response included as an integral part of the process?',
      'review_service_summary.process.author_response.tooltip.answer.yes': 'Yes.',
      'review_service_summary.process.author_response.tooltip.answer.no': 'No.',
      'review_service_summary.process.recommendation.binary': 'Binary decision',
      'review_service_summary.process.recommendation.scale': 'Scalar rating',
      'review_service_summary.process.recommendation.no': 'No decision',
      'review_service_summary.process.recommendation.tooltip.question': 'Does the service provide a decision, recommendation or a scalar rating after the review process?',
      'review_service_summary.process.recommendation.tooltip.answer': 'Post-review decision: {recommendation}.',
      'review_service_summary.policy.title': 'Policy',
      'review_service_summary.policy.guidelines.title': 'Review guidelines:',
      'review_service_summary.policy.guidelines.description_html': 'Yes (<a href="{url}" target="_blank" rel="noopener">read more</a>)',
      'review_service_summary.policy.guidelines.tooltip': 'Online guidelines for reviewers',
      'review_service_summary.policy.coverage.title': 'Review coverage:',
      'review_service_summary.policy.coverage.description': '{review_coverage}',
      'review_service_summary.policy.coverage.tooltip': 'Does the feedback cover the entire paper or only a certain section or aspect?',
      'review_service_summary.policy.identity.title': 'Reviewer identity known to:',
      'review_service_summary.policy.identity.description': '{reviewer_identity_known_to}',
      'review_service_summary.policy.identity.tooltip': 'Are the identities of reviewers known to everyone (public), editors or service, or no one?',
      'review_service_summary.policy.competing_interests.title': 'Competing interests:',
      'review_service_summary.policy.competing_interests.description': '{competing_interests}',
      'review_service_summary.policy.competing_interests.tooltip.question': 'Are competing interests checked and declared?',
      'review_service_summary.policy.competing_interests.tooltip.answer.yes': 'Yes.',
      'review_service_summary.policy.competing_interests.tooltip.answer.no': 'No.',

      /*
       * single-article sub-page
       */
      'single_article.not_found.slug': "The requested article was not found.",
      'single_article.not_found.doi_html': "The article with DOI: <code>{doi}</code> was not found.",

      /*
       * article list sub-page
       */
      'article_list.title': 'Browse',
      'article_list.gt_0.title': '{n} reviewed preprints',
      'article_list.eq_0.title': "Sorry, we couldn't find any results",
      'article_list.eq_0.subtitle': 'Try changing search terms or some of the selected filters.',
      'article_list.sort.by.label': 'Sort by',
      'article_list.sort.by.preprint_date.label': 'preprint date',
      'article_list.sort.by.preprint_date.tooltip': 'Sort by preprint posting date',
      'article_list.sort.by.reviewing_date.label': 'reviewing date',
      'article_list.sort.by.reviewing_date.tooltip': 'Sort by the posting date of the most recent reviews',
      'article_list.sort.order.label': 'Sort order',
      'article_list.sort.order.asc.label': 'oldest first',
      'article_list.sort.order.asc.tooltip': 'Show the oldest postings first',
      'article_list.sort.order.desc.label': 'newest first',
      'article_list.sort.order.desc.tooltip': 'Show the most recent postings first',
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
      'article.figure_keywords.info.message': "All keywords are extracted from this preprint's figure captions. Orange keywords are genes or gene products mentioned in the captions, while green keywords are experimental assays used to observe or measure the assayed components of an experiment.",
      'article.reviews.title': 'Preprint peer review timeline',
      'article.reviews.peer_reviewed_by': 'Reviewed by',
      'article.reviews.summary.title': 'Automated summary of the reviews',
      'article.reviews.summary.info.message': 'This summary was generated automatically using ChatGPT-4 based on the content of the reviews. Currently, this feature is limited to Review Commons reviews. To access the full content of the original reviews, click on "Peer Review".',
      'article.cite.title': 'Cite reviewed preprint',
      'article.cite.btn.tooltip': 'Click to copy reviewed preprint citation',
      'article.cite.text.reviewed_by': 'peer reviewed by <b><i>{service}</i></b>',
      'article.cite.text.citation': '{authors} ({year}). {title}. <b><i>{journal}</i></b> doi.org/{doi}, {reviewedBy} {reviewedPreprintUrl}.',

      /*
       * logo alt texts
       */
      'logo.alt.embo': 'EMBO Logo',

      /*
       * snackbar messages
       */
      'snack.message.copied': 'Text copied to clipboard!',
      'snack.message.error.server': 'An unexpected server error occured. Please try again in a moment...',
      'snack.message.error.request': 'There was an error with your request. Please check your request and try again in a moment...',
    },
  }
})
