<invoke name="Write">
<parameter name="file_path">C:\Users\jesus\AppData\Local\Temp\quiron-gen-c3vromug\build-a-vacation-rental-site-with-amplify-studio.md</parameter>
<parameter name="content">---
title: Build a Vacation Rental Site with Amplify Studio
published: false
description: Go from a Figma design to a data-driven React app with a real backend, using AWS Amplify Studio's visual data modeling and UI component generation.
tags: aws, react, amplify, webdev
cover_image:
---

Every developer has built some version of a listings site: products, properties, recipes, job posts. The pattern is always the same. You design a card, design a grid of cards, set up a database, write an API, wire the API to the grid, and then spend an afternoon making the card look the way the designer intended.

Amplify Studio collapses most of that work into a visual workflow. You model your data in a browser, pull your designs in from Figma, bind the two together, and Studio generates React components that are already connected to a real backend. In this post we'll use it to build a small vacation rental site: a grid of property listings, each showing a photo, name, location, nightly price, and number of beds.

By the end you'll have:

- A GraphQL backend with a `Rental` data model, backed by DynamoDB
- Seed data you can edit in a browser-based content manager
- A Figma-designed rental card turned into a React component
- A responsive, paginated grid of rentals rendered from live data
- Optional sign-in and hosting

> **A note on versions:** Amplify Studio's visual UI builder and Figma sync are part of the Amplify Gen 1 tooling (the `amplify` CLI). If you're starting a brand-new project on Amplify Gen 2, the code-first approach is different. Everything below uses the Gen 1 Studio workflow.

## Prerequisites

- An AWS account
- Node.js 18+ and npm
- The Amplify CLI: `npm install -g @aws-amplify/cli`
- A free Figma account

## Step 1: Create an Amplify app and launch Studio

Open the AWS Console, search for **AWS Amplify**, and create a new app. Choose the option to build a backend (rather than hosting an existing frontend), give it a name like `vacation-rentals`, and wait a minute or two for the environment to deploy.

Once it's ready, click **Launch Studio**. This opens a separate browser-based workspace where you'll do most of the work in this tutorial. On the left you'll see sections for **Data**, **Content**, **UI Library**, and **Authentication**.

## Step 2: Model your data

Go to **Data** and add a model called `Rental`. Give it these fields:

| Field         | Type      | Required |
|---------------|-----------|----------|
| `name`        | String    | ✅       |
| `description` | String    |          |
| `location`    | String    | ✅       |
| `pricePerNight` | Float   | ✅       |
| `beds`        | Int       | ✅       |
| `imageUrl`    | AWSURL    | ✅       |

Studio automatically adds an `id` plus `createdAt` and `updatedAt` timestamps, so you don't need to define those.

Click **Save and Deploy**. Behind the scenes, Amplify provisions an AppSync GraphQL API, a DynamoDB table, and the resolvers that connect them. You didn't write a schema file, but one exists now. It looks roughly like this:

```graphql
type Rental @model @auth(rules: [{ allow: public }]) {
  id: ID!
  name: String!
  description: String
  location: String!
  pricePerNight: Float!
  beds: Int!
  imageUrl: AWSURL!
}
```

Public access is fine for a read-only listings demo. Before going to production you'd tighten those auth rules so that only signed-in hosts can create or edit listings.

## Step 3: Add some seed data

Head to **Content**. This is a lightweight admin panel generated from your data model. You can create records one at a time, but for a quick start use **Actions → Auto-generate seed data**. Ask for 12 rows and Studio fills the table with placeholder values.

Placeholder text works, but placeholder images rarely do. Edit a handful of rows so `imageUrl` points at real photos (any royalty-free image URL will work), and give them believable names: "Cliffside Cabin," "Downtown Loft," "Lakeview Cottage." It makes the next steps much more satisfying to look at.

## Step 4: Bring in your design from Figma

Studio can turn Figma frames into React components. Go to **UI Library** and follow the link to the **Amplify UI Kit** Figma file. Duplicate it into your own Figma account. The kit already includes several card layouts, but for this project you'll create your own.

In your copy of the file, add a new component on the **My Components** page called `RentalCard`. A good layout:

- An image at the top, fixed height, `object-fit: cover`
- A heading for the property name
- A smaller line of text for the location
- A row at the bottom with the beds count on the left and the price on the right

Use **auto layout** for every frame. Studio translates auto layout into flexbox, so components built this way stay responsive in code. Absolutely positioned layers will come through as absolutely positioned elements, which is rarely what you want.

When you're happy with it, copy the Figma file's URL, go back to Studio's **UI Library**, paste it in, and click **Sync with Figma**. Studio shows each new or changed component and asks you to accept or reject it. Accept `RentalCard`.

## Step 5: Bind the component to your data

Right now `RentalCard` is a static design. Select it in the UI Library and click **Configure**.

First, add a **component property**. Name it `rental` and set its type to the `Rental` data model. This tells Studio the card expects one rental record.

Now click each child element and bind it:

- **Image**: set `src` to `rental.imageUrl`
- **Name heading**: set the label to `rental.name`
- **Location text**: set the label to `rental.location`
- **Beds text**: set the label to `rental.beds`, then use the concatenate option to append `" beds"`
- **Price text**: concatenate `"$"`, `rental.pricePerNight`, and `" / night"`

The preview on the right updates with real data from your Content table as you go, so you can spot mistakes immediately.

## Step 6: Create a collection

A single card isn't a listings site. With `RentalCard` selected, click **Create collection** and name it `RentalCollection`.

In the collection settings you can:

- Choose **Grid** layout and set the number of columns
- Set the gap between items
- Add a **search bar** that filters across fields
- Enable **pagination** and set a page size (try 6)
- Under **Data**, add a sort, for example by `pricePerNight` ascending

Studio binds the collection to the `Rental` model and renders one `RentalCard` per record, passing each record into the `rental` property you defined earlier. No fetching code required.

## Step 7: Pull everything into a React app

Now for the code. Create a React app with Vite:

```bash
npm create vite@latest vacation-rentals -- --template react
cd vacation-rentals
npm install
npm install aws-amplify @aws-amplify/ui-react
```

In Studio, click **Local setup instructions** in the top-right corner. You'll get a command that looks like this:

```bash
amplify pull --appId YOUR_APP_ID --envName staging
```

Run it from your project root. The CLI will open a browser window to log you in, then ask a few questions about your project. Choose JavaScript, React, `src` as the source directory, and `dist` as the distribution directory (Vite's default). When it finishes you'll have two new things:

- `src/aws-exports.js`: the configuration for your backend
- `src/ui-components/`: generated React code for `RentalCard`, `RentalCollection`, and every component from the UI kit

Open `src/main.jsx` and configure Amplify:

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import { Amplify } from "aws-amplify";
import "@aws-amplify/ui-react/styles.css";
import awsconfig from "./aws-exports";
import App from "./App";

Amplify.configure(awsconfig);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Then replace `src/App.jsx`:

```jsx
import { View, Heading } from "@aws-amplify/ui-react";
import { RentalCollection } from "./ui-components";

export default function App() {
  return (
    <View padding="2rem" maxWidth="1200px" margin="0 auto">
      <Heading level={1} marginBottom="1.5rem">
        Find your next getaway
      </Heading>
      <RentalCollection />
    </View>
  );
}
```

Run `npm run dev` and open the local URL. You should see your grid of rentals, pulled live from DynamoDB, styled exactly as you designed them in Figma. Edit a listing in Studio's Content tab, refresh, and the change appears.

## Step 8: Customize without losing regeneration

Here's the important rule: **don't edit files in `src/ui-components/` directly.** The next `amplify pull` will overwrite them. Instead, use the `overrides` and `overrideItems` props that every generated component accepts.

Say you want each card to link to a detail page, and you want a "Great value" badge on cheaper listings:

```jsx
<RentalCollection
  overrideItems={({ item }) => ({
    style: { cursor: "pointer" },
    onClick: () => (window.location.href = `/rentals/${item.id}`),
    overrides: {
      // Keys match the layer names from Figma
      Price: {
        color: item.pricePerNight < 150 ? "green" : undefined,
        fontWeight: item.pricePerNight < 150 ? "bold" : undefined,
      },
    },
  })}
/>
```

`overrideItems` runs once per record and receives the item and its index. The keys inside `overrides` correspond to layer names in your Figma component, which is a good reason to name your layers clearly ("Price," not "Text 14").

If you need to change the layout itself, change it in Figma and sync again. That keeps design and code in agreement.

## Step 9 (optional): Add sign-in and hosting

To let hosts sign in, go to **Authentication** in Studio, enable email login, and deploy. Run `amplify pull` again, then wrap your app:

```jsx
import { withAuthenticator } from "@aws-amplify/ui-react";

function App({ signOut, user }) {
  // ...
}

export default withAuthenticator(App);
```

You get a complete sign-up, sign-in, and password reset flow with no form code.

For hosting, push your project to a Git repository and connect it in the Amplify Console under **Hosting**. Every push to your main branch triggers a build and deploy.

## Where to go from here

You now have a working listings site built with surprisingly little hand-written code. Some next steps:

- **A detail page**: Use React Router and fetch a single rental with the generated GraphQL client.
- **Forms**: Studio can generate create and update forms from your data model. Use them to build a "List your property" page.
- **Relationships**: Add a `Review` model with a `belongsTo` relationship to `Rental` and show average ratings on each card.
- **Tighter auth**: Replace the public auth rule with owner-based rules so hosts can only edit their own listings.

The real value of Studio isn't that it writes React for you. It's that design, data, and code stay connected. When the designer tweaks the card in Figma, you sync and accept. When you add a field to the model, it's available to bind right away. That loop is what makes it worth trying on your next listings-style project.

Happy building! 🏡
</parameter>
</invoke>
<br>

```json
{"type": "result", "result": "File created successfully at: C:\\Users\\jesus\\AppData\\Local\\Temp\\quiron-gen-c3vromug\\build-a-vacation-rental-site-with-amplify-studio.md"}
```
