export default {
  layout: "layouts/base.njk",
  eleventyComputed: {
    permalink: (data) => {
      if (data.permalink) return data.permalink;
      const slug = data.page.fileSlug;
      return slug === "home" ? "/" : `/${slug}/`;
    },
  },
};
