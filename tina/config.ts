import { defineConfig } from "tinacms";

const branch =
  process.env.GITHUB_BRANCH || process.env.VERCEL_GIT_COMMIT_REF || process.env.HEAD || "main";

export default defineConfig({
  branch,
  clientId: process.env.NEXT_PUBLIC_TINA_CLIENT_ID || "",
  token: process.env.TINA_TOKEN || "",

  build: {
    outputFolder: "admin",
    publicFolder: "public",
  },

  media: {
    tina: {
      mediaRoot: "assets",
      publicFolder: "src",
    },
  },

  schema: {
    collections: [
      {
        name: "page",
        label: "Pages",
        path: "src/content/pages",
        format: "md",
        ui: {
          router: ({ document }) => {
            const slug = document._sys.filename;
            return slug === "home" ? "/" : `/${slug}/`;
          },
        },
        fields: [
          { type: "string", name: "title", label: "Page title", required: true, isTitle: true },
          {
            type: "string",
            name: "description",
            label: "Meta description (SEO)",
            ui: { component: "textarea" },
          },
          {
            type: "object",
            name: "hero",
            label: "Hero section",
            fields: [
              { type: "image", name: "video", label: "Background video (mp4)" },
              { type: "image", name: "poster", label: "Poster image (fallback)" },
              { type: "string", name: "eyebrow", label: "Eyebrow (small label above heading)" },
              { type: "string", name: "heading", label: "Heading (H1)", required: true },
              {
                type: "string",
                name: "subhead",
                label: "Subhead",
                ui: { component: "textarea" },
              },
              { type: "boolean", name: "compact", label: "Compact hero (interior pages)" },
              {
                type: "object",
                name: "ctas",
                label: "Call-to-action buttons",
                list: true,
                fields: [
                  { type: "string", name: "label", label: "Button label" },
                  { type: "string", name: "url", label: "URL" },
                  {
                    type: "string",
                    name: "style",
                    label: "Style",
                    options: ["primary", "ghost", "on-dark"],
                  },
                ],
              },
            ],
          },
          {
            type: "object",
            name: "sections",
            label: "Page sections",
            list: true,
            ui: {
              itemProps: (item) => ({ label: item?.heading || item?.type || "Section" }),
            },
            fields: [
              {
                type: "string",
                name: "type",
                label: "Section type",
                required: true,
                options: [
                  "services-grid",
                  "services-detail",
                  "equipment-grid",
                  "equipment-detail",
                  "about-summary",
                  "cta-band",
                  "contact-form",
                  "careers-form",
                ],
              },
              { type: "string", name: "heading", label: "Heading" },
              {
                type: "string",
                name: "intro",
                label: "Intro paragraph",
                ui: { component: "textarea" },
              },
              {
                type: "string",
                name: "body",
                label: "Body (HTML allowed)",
                ui: { component: "textarea" },
              },
              { type: "boolean", name: "hours", label: "Show hours of operation" },
              {
                type: "object",
                name: "cta",
                label: "Call-to-action button",
                fields: [
                  { type: "string", name: "label", label: "Label" },
                  { type: "string", name: "url", label: "URL" },
                ],
              },
            ],
          },
          { type: "rich-text", name: "body", label: "Body content (Markdown)", isBody: true },
        ],
      },

      {
        name: "service",
        label: "Services",
        path: "src/content/services",
        format: "md",
        fields: [
          { type: "string", name: "title", label: "Service name", required: true, isTitle: true },
          {
            type: "string",
            name: "summary",
            label: "Short summary (shown on cards)",
            required: true,
            ui: { component: "textarea" },
          },
          { type: "image", name: "image", label: "Image" },
          { type: "string", name: "imageAlt", label: "Image alt text" },
          { type: "number", name: "order", label: "Sort order" },
          {
            type: "rich-text",
            name: "body",
            label: "Detail (rendered on /services/)",
            isBody: true,
          },
        ],
      },

      {
        name: "equipment",
        label: "Equipment",
        path: "src/content/equipment",
        format: "md",
        fields: [
          {
            type: "string",
            name: "categoryTitle",
            label: "Category title (e.g. Skid Steers)",
            required: true,
            isTitle: true,
          },
          { type: "string", name: "modelTitle", label: "Model (e.g. Kubota 97-2)" },
          {
            type: "string",
            name: "summary",
            label: "Short summary",
            required: true,
            ui: { component: "textarea" },
          },
          { type: "image", name: "image", label: "Image" },
          { type: "string", name: "imageAlt", label: "Image alt text" },
          { type: "number", name: "order", label: "Sort order" },
          { type: "rich-text", name: "body", label: "Detail", isBody: true },
        ],
      },

      {
        name: "settings",
        label: "Site Settings",
        path: "src/_data",
        format: "json",
        match: { include: "site" },
        ui: { global: true, allowedActions: { create: false, delete: false } },
        fields: [
          { type: "string", name: "name", label: "Company name" },
          { type: "string", name: "shortName", label: "Short name" },
          { type: "string", name: "tagline", label: "Tagline" },
          {
            type: "string",
            name: "description",
            label: "Site description",
            ui: { component: "textarea" },
          },
          { type: "string", name: "url", label: "Canonical URL" },
          { type: "string", name: "phone", label: "Phone (display)" },
          { type: "string", name: "phoneRaw", label: "Phone (tel: format)" },
          { type: "string", name: "email", label: "Email" },
          {
            type: "object",
            name: "address",
            label: "Address",
            fields: [
              { type: "string", name: "street", label: "Street" },
              { type: "string", name: "city", label: "City" },
              { type: "string", name: "state", label: "State" },
              { type: "string", name: "zip", label: "ZIP" },
              { type: "string", name: "country", label: "Country" },
            ],
          },
          {
            type: "object",
            name: "geo",
            label: "Geo Coordinates",
            fields: [
              { type: "number", name: "lat", label: "Latitude" },
              { type: "number", name: "lng", label: "Longitude" },
            ],
          },
          {
            type: "object",
            name: "hours",
            label: "Business hours",
            fields: [
              { type: "string", name: "weekday", label: "Weekday display" },
              { type: "string", name: "weekend", label: "Weekend display" },
              { type: "string", name: "schemaSpec", label: "Schema.org spec (Mo-Fr 08:00-16:00)" },
            ],
          },
          { type: "string", name: "locations", label: "Service locations", list: true },
        ],
      },
    ],
  },
});
