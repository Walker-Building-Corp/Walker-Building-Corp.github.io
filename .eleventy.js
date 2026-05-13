export default function (eleventyConfig) {
  // The site is a faithful HTML mirror of the live walkerbldgcorp.com.
  // Pages are .njk templates under src/content/pages/ with raw markup.
  // Tina edits sitewide values in src/_data/site.json (referenced by templates that need it).

  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/robots.txt": "robots.txt" });
  eleventyConfig.addPassthroughCopy({ "src/_headers": "_headers" });
  eleventyConfig.addPassthroughCopy({ "src/_redirects": "_redirects" });

  eleventyConfig.addFilter("isoDate", (d) =>
    (d instanceof Date ? d : new Date(d)).toISOString()
  );

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "public",
    },
    templateFormats: ["njk", "md", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
}
