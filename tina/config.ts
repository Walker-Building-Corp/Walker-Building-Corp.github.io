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
      mediaRoot: "assets/vendor/img",
      publicFolder: "public",
    },
  },

  schema: {
    collections: [
      {
        // Single editable document for sitewide settings (phone, email, address, hours).
        // The page templates are an HTML mirror of the live site and aren't field-editable;
        // structural changes happen in the .njk templates under src/content/pages/.
        name: "settings",
        label: "Site Settings",
        path: "src/_data",
        format: "json",
        match: { include: "site" },
        ui: {
          global: true,
          allowedActions: { create: false, delete: false },
        },
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
          { type: "string", name: "phoneRaw", label: "Phone (tel: format, e.g. +13525551212)" },
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
            name: "hours",
            label: "Business Hours",
            fields: [
              { type: "string", name: "weekday", label: "Weekday display" },
              { type: "string", name: "weekend", label: "Weekend display" },
            ],
          },
          { type: "string", name: "locations", label: "Service locations", list: true },
        ],
      },
    ],
  },
});
