# Build a Vacation Rental Site with Amplify Studio

If you've ever wanted to spin up a full-stack app without spending a week wiring together a backend, a database, and a UI component library, AWS Amplify Studio is worth a look. It's a visual development environment that lets you model data, design UI in Figma, and generate React components that are already connected to your backend.

In this tutorial, we'll build a simple vacation rental listing site. Users will be able to browse rental properties, see details like price and location, and we'll manage the data from a visual admin panel. By the end, you'll have a deployed React app backed by a real database.

## What we're building

Our app will have:

- A data model for rental listings (name, location, price, image, description)
- A grid of listing cards generated from Figma designs
- Seed data managed through Amplify Studio's content manager
- A React frontend that pulls live data from the backend

## Prerequisites

You'll need:

- An AWS account
- Node.js (v14 or later) and npm
- The Amplify CLI: `npm install -g @aws-amplify/cli`
- A Figma account (free is fine)

## Step 1: Create an Amplify Studio app

Head to the AWS Amplify console and click **New app** → **Build an app**. Give it a name like `vacation-rentals` and confirm the deployment. Amplify will take a minute or two to provision the environment.

Once it's ready, click **Launch Studio**. This opens the Amplify Studio interface, which is where we'll do most of the backend work.

## Step 2: Model your data

In the left sidebar, click **Data**. This is where you define your data model visually, and Amplify will generate a GraphQL API and DynamoDB tables behind the scenes.

Click **Add model** and name it `Rental`. Then add these fields:

| Field | Type |
|-------|------|
| `name` | String |
| `location` | String |
| `price` | Int |
| `image` | AWSURL |
| `description` | String |

Amplify automatically adds an `id` field, plus `createdAt` and `updatedAt` timestamps.

Click **Save and Deploy**. This step provisions an AppSync GraphQL API and a DynamoDB table for your rentals. It can take a few minutes.

## Step 3: Add some seed data

While you're in Studio, go to **Content** in the sidebar. This is a built-in admin panel for your data. You can click **Auto-generate seed data** to fill the table with fake listings, or add a few by hand.

I'd recommend adding at least a few entries manually with real image URLs (Unsplash works well) so the final site actually looks like a vacation rental site. Something like:

- **Cozy Mountain Cabin**, Aspen, CO, $250/night
- **Beachfront Bungalow**, Tulum, Mexico, $180/night
- **Downtown Loft**, Lisbon, Portugal, $140/night

## Step 4: Design your UI in Figma

This is where Amplify Studio really stands out. Go to **UI Library** in the sidebar and click **Get started**. Amplify will give you a link to its Figma file, which is a pre-built component kit that includes cards, navbars, and other common UI elements.

Duplicate that file into your own Figma account. You can use the components as-is or customize them. For our site, the `RentalCard` or `CardA` style components work nicely out of the box. Feel free to tweak colors, fonts, or spacing.

When you're ready, copy the Figma file's URL and paste it back into Amplify Studio. Studio will import all your components and show them in the UI Library.

## Step 5: Bind data to components

Pick a card component from the UI Library and click **Configure**. Here, you can bind component properties to your data model.

1. Click **Add prop** and create a prop called `rental` of type `Rental`.
2. Click on the image element in the card and set its `src` to `rental.image`.
3. Set the title text to `rental.name`.
4. Set the subtitle to `rental.location`.
5. Set the price text to `rental.price`. You can concatenate strings here to show something like `$250/night`.

Next, create a collection. Click **Create collection** from the component, name it `RentalCollection`, and choose a grid layout. You can set the number of columns, spacing, and even enable pagination or search. Studio shows you a live preview using the data you seeded earlier.

## Step 6: Set up the React app

Now let's create the frontend:

```bash
npx create-react-app vacation-rentals
cd vacation-rentals
npm install aws-amplify @aws-amplify/ui-react
```

Back in Amplify Studio, click **Local setup instructions** in the top right. It'll give you a command that looks like this:

```bash
amplify pull --appId YOUR_APP_ID --envName staging
```

Run it in your project folder. Log in when prompted and accept the defaults. This pulls down your backend config and generates the UI components into `src/ui-components`.

## Step 7: Configure Amplify in your app

Open `src/index.js` and configure Amplify:

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

import { Amplify } from 'aws-amplify';
import { AmplifyProvider } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import config from './aws-exports';

Amplify.configure(config);

ReactDOM.render(
  <AmplifyProvider>
    <App />
  </AmplifyProvider>,
  document.getElementById('root')
);
```

## Step 8: Render the collection

Now open `src/App.js` and replace its contents:

```javascript
import { RentalCollection } from './ui-components';

function App() {
  return (
    <div className="App">
      <h1>Find Your Next Getaway</h1>
      <RentalCollection />
    </div>
  );
}

export default App;
```

That's genuinely all the code you need to render a grid of listings from your database. Run `npm start` and you should see your rental cards populated with the data you added in Studio.

## Step 9: Add a navbar (optional)

The Figma kit includes a navbar component too. If you imported it, you can drop it in:

```javascript
import { NavBar, RentalCollection } from './ui-components';

function App() {
  return (
    <div className="App">
      <NavBar width="100%" />
      <RentalCollection />
    </div>
  );
}
```

You can override props on any generated component. For example, to change a link in the navbar or add click handlers, use the `overrides` prop:

```javascript
<NavBar
  width="100%"
  overrides={{
    Logo: { children: 'StayAway' },
  }}
/>
```

## Step 10: Deploy

To host the site, run:

```bash
amplify add hosting
```

Choose **Hosting with Amplify Console** and **Manual deployment**. Then:

```bash
amplify publish
```

After a few minutes, you'll get a live URL for your vacation rental site.

## Making changes

One of the nicest parts of this workflow is iteration. If a designer changes a component in Figma, you can click **Sync with Figma** in Studio and run `amplify pull` again to get the updated components. If you add a new field to your data model, say `bedrooms`, you can update it in Studio, redeploy, and bind the new field to your card.

One caveat: generated files in `ui-components` get overwritten on each pull, so don't edit them directly. Use `overrides` or wrap them in your own components instead.

## Wrapping up

In this tutorial we:

- Modeled data visually and deployed a GraphQL API with DynamoDB
- Seeded data through the Studio content manager
- Designed UI in Figma and turned it into React components
- Bound those components to live data
- Deployed the whole thing to a public URL

Amplify Studio won't replace hand-written code for every use case, but for getting a data-driven app off the ground quickly, it removes a lot of the boilerplate. From here, you could add authentication so hosts can create their own listings, a detail page for each rental, or a booking form. Happy building!
