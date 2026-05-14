import { execSync } from "node:child_process";

export default function (eleventyConfig) {
  // Static-asset passthrough.
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/robots.txt": "robots.txt" });
  eleventyConfig.addPassthroughCopy({ "src/_headers": "_headers" });
  eleventyConfig.addPassthroughCopy({ "src/_redirects": "_redirects" });

  // Collections: services and equipment, ordered by frontmatter `order`.
  eleventyConfig.addCollection("services", (api) =>
    api
      .getFilteredByGlob("src/content/services/*.md")
      .sort((a, b) => (a.data.order ?? 0) - (b.data.order ?? 0))
  );
  eleventyConfig.addCollection("equipment", (api) =>
    api
      .getFilteredByGlob("src/content/equipment/*.md")
      .sort((a, b) => (a.data.order ?? 0) - (b.data.order ?? 0))
  );

  // Filters.
  eleventyConfig.addFilter("isoDate", (d) => (d instanceof Date ? d : new Date(d)).toISOString());

  // Returns the file's last git-commit ISO timestamp for stable sitemap lastmod.
  // Falls back to the page's own date if the file isn't tracked.
  eleventyConfig.addFilter("gitLastModified", function (inputPath) {
    try {
      const iso = execSync(`git log -1 --format=%cI -- "${inputPath}"`, {
        encoding: "utf8",
      }).trim();
      if (iso) return iso;
    } catch {
      // fall through
    }
    return new Date().toISOString();
  });

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
