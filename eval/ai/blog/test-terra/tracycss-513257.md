# A React website with Styled-components for beginners ✨

Building your first React website is exciting—until you start wondering where all the CSS should go. You could use a single stylesheet, create a CSS file for every component, or try a library that lets you write styles alongside your JavaScript.

In this tutorial, we’ll use **styled-components** to build a small, responsive landing page. Along the way, you’ll learn how to create styled elements, pass props to them, reuse styles, and adapt the layout for smaller screens.

You don’t need to be a React expert. Basic familiarity with HTML, CSS, and JavaScript will help, but we’ll walk through each step.

## What is styled-components?

Styled-components is a library that lets you write CSS for individual React components.

Instead of creating a CSS class and attaching it to an element, you create a styled component:

```jsx
import styled from "styled-components";

const Title = styled.h1`
  color: rebeccapurple;
  font-size: 2rem;
`;
```

You can then use it like any other React component:

```jsx
<Title>Hello, React!</Title>
```

`Title` renders as an `<h1>` with the styles you defined. Styled-components generates and manages the CSS class behind the scenes.

This approach can be useful because the styles for a component live close to the component itself. It also makes it easy to change styles based on props.

## What we’re building

Our example will be a landing page for an imaginary creative community called **Spark**. It will include:

- A navigation bar
- A hero section with a call to action
- Three feature cards
- A responsive layout

By the end, you’ll have a small site you can customize with your own text, colors, and components.

## 1. Set up a React project

If you already have a React project, you can skip to installing styled-components.

For a new project, create one with Vite:

```bash
npm create vite@latest spark-site -- --template react
cd spark-site
npm install
```

Then install styled-components:

```bash
npm install styled-components
```

Start the development server:

```bash
npm run dev
```

Open the local URL shown in your terminal. You should see the starter React page.

We’ll replace the starter content as we build. In `src/main.jsx`, make sure your app is rendered like this:

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## 2. Add global styles and a theme

Most styles in this tutorial will belong to individual components. A few styles, such as the page background and default font, make sense globally.

We’ll also create a theme so we can reuse colors and spacing values. Create a file named `src/styles.js`:

```jsx
import { createGlobalStyle } from "styled-components";

export const theme = {
  colors: {
    background: "#f8f7ff",
    surface: "#ffffff",
    text: "#24213d",
    muted: "#625f78",
    primary: "#6c4df6",
    primaryDark: "#5133d6",
    border: "#e7e4f5",
  },
  radius: "16px",
};

export const GlobalStyle = createGlobalStyle`
  *, *::before, *::after {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: system-ui, -apple-system, sans-serif;
    color: ${({ theme }) => theme.colors.text};
    background: ${({ theme }) => theme.colors.background};
    line-height: 1.5;
  }

  a {
    color: inherit;
  }
`;
```

The syntax `${({ theme }) => theme.colors.text}` is a JavaScript expression inside a tagged template literal. Styled-components evaluates it and uses the result as a CSS value.

Next, we’ll give our app access to the theme using `ThemeProvider`.

## 3. Create the page structure

Open `src/App.jsx` and replace its contents with the following imports and components:

```jsx
import styled, { ThemeProvider } from "styled-components";
import { GlobalStyle, theme } from "./styles";

const Page = styled.div`
  min-height: 100vh;
`;

const Container = styled.div`
  width: min(100% - 2rem, 1100px);
  margin-inline: auto;
`;

const Header = styled.header`
  padding-block: 1.5rem;
`;

const Navigation = styled.nav`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
`;

const Logo = styled.a`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 1.5rem;
  font-weight: 800;
  text-decoration: none;
`;

const NavLink = styled.a`
  font-weight: 600;
  text-decoration: none;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;
```

These components render familiar HTML elements: `Page` is a `<div>`, `Header` is a `<header>`, and so on.

The `&:hover` selector refers to the styled element itself when a user hovers over it. If you’ve used a CSS preprocessor before, the nesting may look familiar.

Now add the React component below those definitions:

```jsx
function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />

      <Page>
        <Header>
          <Container>
            <Navigation aria-label="Main navigation">
              <Logo href="#">✨ Spark</Logo>
              <NavLink href="#features">Features</NavLink>
            </Navigation>
          </Container>
        </Header>

        <main>
          <Container>
            <h1>Make room for your next idea.</h1>
            <p>A friendly place to learn, create, and grow.</p>
          </Container>
        </main>
      </Page>
    </ThemeProvider>
  );
}

export default App;
```

Save the file and check your browser. You should see a simple header and some introductory text.

`ThemeProvider` makes the theme available to styled components inside it. That’s why our `Logo` and global styles can read values from `theme.colors`.

## 4. Build the hero section

Let’s give the main introduction a more welcoming layout. Add these styled components **above** the `App` function:

```jsx
const Hero = styled.section`
  padding-block: 5rem;

  @media (max-width: 600px) {
    padding-block: 3rem;
  }
`;

const Eyebrow = styled.p`
  color: ${({ theme }) => theme.colors.primary};
  font-weight: 700;
`;

const HeroTitle = styled.h1`
  max-width: 14ch;
  margin: 0;
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  line-height: 1.1;
  letter-spacing: -0.04em;
`;

const HeroText = styled.p`
  max-width: 55ch;
  margin-block: 1.5rem 2rem;
  color: ${({ theme }) => theme.colors.muted};
  font-size: 1.15rem;
`;

const ButtonLink = styled.a`
  display: inline-block;
  padding: 0.85rem 1.25rem;
  border-radius: 999px;
  background: ${({ theme }) => theme.colors.primary};
  color: white;
  font-weight: 700;
  text-decoration: none;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryDark};
  }

  &:focus-visible {
    outline: 3px solid ${({ theme }) => theme.colors.text};
    outline-offset: 3px;
  }
`;
```

A couple of CSS details are doing useful work here:

- `clamp()` lets the heading grow with the viewport while keeping it within a minimum and maximum size.
- The media query reduces vertical spacing on smaller screens.
- `:focus-visible` gives keyboard users a visible indicator when they navigate to the link.

Replace the `<Container>` inside `<main>` with:

```jsx
<Container>
  <Hero>
    <Eyebrow>Ideas start here ✨</Eyebrow>
    <HeroTitle>Make room for your next idea.</HeroTitle>
    <HeroText>
      Spark is a friendly place to learn new skills, share your work,
      and create alongside curious people.
    </HeroText>
    <ButtonLink href="#features">Explore Spark</ButtonLink>
  </Hero>
</Container>
```

We’re using an anchor styled as a button because it takes the visitor to another part of the page. For an action such as submitting a form, use a `<button>` instead.

## 5. Add feature cards

Next, let’s show visitors what the community offers. Add these styled components above `App`:

```jsx
const Features = styled.section`
  padding-bottom: 5rem;
`;

const SectionTitle = styled.h2`
  margin-top: 0;
  font-size: 2rem;
`;

const CardGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;

  @media (max-width: 700px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.article`
  padding: 1.5rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radius};
  background: ${({ theme }) => theme.colors.surface};
`;

const CardIcon = styled.span`
  display: inline-block;
  font-size: 1.75rem;
`;

const CardTitle = styled.h3`
  margin-bottom: 0.5rem;
`;

const CardText = styled.p`
  margin-bottom: 0;
  color: ${({ theme }) => theme.colors.muted};
`;
```

The grid displays three columns on wider screens and stacks the cards below 700 pixels.

We can keep the card content in an array. Add this above the `App` function too:

```jsx
const features = [
  {
    icon: "📚",
    title: "Learn together",
    description: "Find practical resources and build skills at your own pace.",
  },
  {
    icon: "🎨",
    title: "Share your work",
    description: "Bring your ideas to life and celebrate your progress.",
  },
  {
    icon: "💬",
    title: "Meet curious people",
    description: "Connect with others who love making and learning.",
  },
];
```

Inside the `<Container>`, immediately after the closing `</Hero>` tag, add:

```jsx
<Features id="features">
  <SectionTitle>A little spark goes a long way</SectionTitle>

  <CardGrid>
    {features.map((feature) => (
      <Card key={feature.title}>
        <CardIcon aria-hidden="true">{feature.icon}</CardIcon>
        <CardTitle>{feature.title}</CardTitle>
        <CardText>{feature.description}</CardText>
      </Card>
    ))}
  </CardGrid>
</Features>
```

React’s `map()` creates a card for each item. The `key` helps React identify items in the list. Here, each title is unique, so it works as a key.

The emoji are marked `aria-hidden` because the card titles already communicate their meaning.

## 6. Change styles with props

One useful feature of styled-components is that styles can depend on props. Let’s give one card a subtle highlight.

Update the `Card` definition:

```jsx
const Card = styled.article`
  padding: 1.5rem;
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.radius};
  background: ${({ $featured, theme }) =>
    $featured ? "#efecff" : theme.colors.surface};
`;
```

Then update the opening `Card` tag inside `map()`:

```jsx
<Card key={feature.title} $featured={feature.title === "Share your work"}>
```

The `$featured` prop controls the background color. The `$` prefix makes it a **transient prop**, which tells styled-components to use it for styling without forwarding it to the HTML element.

You can use the same idea for variations such as button sizes, alert colors, or selected states. Keep the number of variations manageable so components remain easy to understand.

## 7. Try your own changes

You now have a complete little landing page! Resize the browser to see the cards stack, and use the Tab key to check the call-to-action link’s focus style.

Here are a few ways to make the project your own:

1. Change the colors in `theme` and see how the site updates.
2. Add another feature to the array.
3. Create a footer with links to your own projects.
4. Add an image to the hero section, with meaningful alternative text.
5. Split the header, hero, and cards into separate component files as the app grows.

Styled-components gives you a way to keep styles close to the elements they describe while still writing familiar CSS. Start with small components, use a theme for repeated values, and experiment—you’ll quickly find a structure that feels comfortable for your projects.

Happy building! ✨
