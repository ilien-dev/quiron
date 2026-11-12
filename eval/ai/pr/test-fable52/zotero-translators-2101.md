## Summary

ACM Digital Library has moved to a new platform, and the existing translator no longer works there: the old `citation.cfm` URLs, page structure, and BibTeX export endpoints are gone. This PR rewrites `ACM Digital Library.js` from scratch for the new site.

## Changes

- **Detection**: matches the new `/doi/` URL scheme (including `/doi/abs/`, `/doi/full/`, and `/doi/pdf/`) and determines item type from the page metadata rather than from breadcrumbs. Search results, tables of contents, and author profile pages are detected as `multiple`.
- **Metadata**: looks up the DOI through the site's citation export endpoint, which returns CSL JSON, and imports it instead of scraping the page. This replaces the old BibTeX-based flow and its regex cleanup.
- **Supplemental scraping**: abstract, keywords, and page count are taken from the page, since the export omits them.
- **Attachments**: PDFs are attached using the new `/doi/pdf/` path when the full text is available.
- **Cleanup**: removed the legacy code paths, switched to `async`/`await` and `requestJSON`/`requestDocument`, and passed ESLint.

## Testing

Test cases were replaced with new-site URLs covering a journal article, a conference paper, a book, a book chapter, a thesis, and a search results page. All pass in Scaffold on Firefox and Chrome.

## Notes

Old-format URLs redirect to the new site, so no legacy handling is retained.
