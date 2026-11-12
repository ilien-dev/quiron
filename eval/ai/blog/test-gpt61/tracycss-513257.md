# A React website with Styled-components for beginners ✨

Building your first React website is exciting—until your styles start getting tangled. A button looks perfect on one page, then a CSS rule changes every other button. Class names pile up, and finding the right stylesheet becomes a small detective mission.

Styled-components gives you another way to organize those styles: attach them directly to reusable React components.

In this tutorial, we’ll build a simple portfolio website with a navigation bar, an introduction, and project cards. Along the way, you’ll learn how to write styled components, change their appearance with props, and make your layout responsive.

You’ll need basic HTML, CSS, and JavaScript knowledge. Some familiarity with React components will help, but we’ll explain the important pieces as we go.

Let’s build something! 🚀

## 1. What is styled-components?

Styled-components is a CSS-in-JS library. It lets you write CSS inside JavaScript files and use the result as React components.

Here’s a small example:

```jsx
import styled from "styled-components";

const Heading = styled.h1`
  color: #6d28d9;
  font-size: 3rem;
`;

export default function App() {
  return <Heading>Hello, developer!</Heading>;
}
```

`Heading` renders an HTML `<h1>` with the styles we defined.

The backticks contain a **tagged template literal**. You don’t need to master that JavaScript feature to get started; for now, think of this as a place to write CSS.

Styled-components generates class names for your components, helping keep their styles separate. You still use familiar CSS properties, selectors, and media queries. The [official introduction](https://styled-components.com/docs) explains how this works.

## 2. Create your React project

First, install Node.js and npm if you haven’t already. Use a Node.js version supported by the current [Vite requirements](https://vite.dev/guide/).

Open your terminal and run:

```bash
npm create vite@latest beginner-portfolio -- --template react
cd beginner-portfolio
npm install
npm install styled-components
npm run dev
```

Open the local URL printed in your terminal.

Vite provides the development server and build tools for this project. React’s documentation includes Vite as an option for [learning React from scratch](https://react.dev/learn/build-a-react-app-from-scratch).

Inside `src`, we’ll work with three files:

```text
src/
├── App.jsx
├── GlobalStyles.js
└── main.jsx
```

You can leave unused starter assets alone, but remove the starter CSS imports when replacing the files below. Otherwise, those styles may affect your design.

## 3. Set up global styles

Most styles should belong to individual components. However, some rules apply across the website, such as the body font and default spacing.

Create `src/GlobalStyles.js`:

```jsx
import { createGlobalStyle } from "styled-components";

const GlobalStyles = createGlobalStyle`
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f7f7fc;
    color: #202033;
    line-height: 1.6;
  }

  a {
    color: inherit;
  }

  button,
  input,
  textarea {
    font: inherit;
  }
`;

export default GlobalStyles;
```

`createGlobalStyle` creates a component that applies global CSS when rendered.

The `box-sizing` rule makes dimensions easier to manage: padding and borders are included in an element’s declared width.

Now replace `src/main.jsx` with:

```jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import GlobalStyles from "./GlobalStyles.js";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <GlobalStyles />
    <App />
  </StrictMode>
);
```

Notice that this file doesn’t import the starter `index.css`.

## 4. Create your page components

Replace everything in `src/App.jsx` with the following:

```jsx
import styled from "styled-components";

const Container = styled.div`
  width: min(1100px, 92%);
  margin: 0 auto;
`;

const Header = styled.header`
  padding: 1.5rem 0;
  border-bottom: 1px solid #ddddea;
`;

const Navigation = styled.nav`
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
`;

const Logo = styled.a`
  color: #6d28d9;
  font-size: 1.4rem;
  font-weight: 800;
  text-decoration: none;
`;

const NavLink = styled.a`
  text-decoration: none;

  &:hover {
    color: #6d28d9;
    text-decoration: underline;
  }

  &:focus-visible {
    outline: 3px solid #6d28d9;
    outline-offset: 4px;
  }
`;

const Hero = styled.section`
  padding: 5rem 0;
  max-width: 720px;

  h1 {
    margin: 0 0 1rem;
    font-size: clamp(2.5rem, 7vw, 4.5rem);
    line-height: 1.1;
  }

  p {
    margin-bottom: 2rem;
    color: #55556b;
    font-size: 1.15rem;
  }
`;

const ActionLink = styled.a`
  display: inline-block;
  padding: 0.8rem 1.2rem;
  border: 2px solid #6d28d9;
  border-radius: 0.75rem;
  background: ${({ $primary }) =>
    $primary ? "#6d28d9" : "transparent"};
  color: ${({ $primary }) =>
    $primary ? "#ffffff" : "#6d28d9"};
  font-weight: 700;
  text-decoration: none;

  &:hover {
    background: #5520aa;
    border-color: #5520aa;
    color: white;
  }

  &:focus-visible {
    outline: 3px solid #202033;
    outline-offset: 4px;
  }
`;

const ProjectsSection = styled.section`
  padding-bottom: 4rem;
`;

const ProjectGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;

  @media (max-width: 800px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.article`
  padding: 1.5rem;
  border: 1px solid #ddddea;
  border-radius: 1rem;
  background: white;
  box-shadow: 0 8px 24px rgb(32 32 51 / 6%);

  h3 {
    margin-top: 0;
  }

  p {
    color: #55556b;
  }
`;

const Footer = styled.footer`
  padding: 2rem 0;
  border-top: 1px solid #ddddea;
  color: #55556b;
`;

const projects = [
  {
    id: "weather",
    title: "Weather app",
    description: "A project for practicing API requests.",
  },
  {
    id: "recipes",
    title: "Recipe collection",
    description: "A place to organize my favorite meals.",
  },
  {
    id: "tasks",
    title: "Task tracker",
    description: "A small app for learning React state.",
  },
];

export default function App() {
  return (
    <>
      <Header>
        <Container>
          <Navigation aria-label="Main navigation">
            <Logo href="#">Alex.dev</Logo>
            <NavLink href="#projects">My projects</NavLink>
          </Navigation>
        </Container>
      </Header>

      <Container as="main">
        <Hero aria-labelledby="intro-title">
          <h1 id="intro-title">
            Hi, I’m Alex. I build things for the web.
          </h1>
          <p>
            I’m learning React and turning small ideas
            into useful, accessible websites.
          </p>
          <ActionLink href="#projects" $primary>
            Explore my projects
          </ActionLink>
        </Hero>

        <ProjectsSection
          id="projects"
          aria-labelledby="projects-title"
        >
          <h2 id="projects-title">Recent projects</h2>

          <ProjectGrid>
            {projects.map((project) => (
              <Card key={project.id}>
                <h3>{project.title}</h3>
                <p>{project.description}</p>
              </Card>
            ))}
          </ProjectGrid>
        </ProjectsSection>
      </Container>

      <Footer>
        <Container>
          Built with React, styled-components, and curiosity.
        </Container>
      </Footer>
    </>
  );
}
```

Save your changes. You should now have a complete portfolio layout.

There’s a lot in that file, so let’s unpack the useful parts.

## 5. Understand the styling patterns

### Components are reusable building blocks

`Container` keeps the page content centered and limits its width.

We use it inside the header, main content, and footer. Updating its width changes all three areas consistently.

The `as="main"` prop changes that instance’s underlying element from a `<div>` to a `<main>`, while keeping its styles. Choosing meaningful HTML helps describe your page’s structure.

### Nested selectors keep related styles together

Inside `Hero`, we style its headings and paragraphs:

```css
h1 {
  margin: 0 0 1rem;
}
```

This targets headings inside that component instead of every heading across the website.

The `&` character refers to the styled component itself. For example, `&:hover` applies when someone hovers over that element.

These patterns are covered in the [styled-components basics guide](https://styled-components.com/docs/basics).

### Props can change appearance

Our call-to-action uses `$primary` to choose its colors:

```jsx
<ActionLink href="#projects" $primary>
  Explore my projects
</ActionLink>
```

Without `$primary`, the same component renders with a transparent background and purple text.

The `$` prefix makes this a **transient prop**: styled-components uses it for styling without forwarding it to the HTML element. See the [transient props documentation](https://styled-components.com/docs/api#transient-props) for details.

Also notice that this component is an anchor. It navigates to another location on the page, so a link is appropriate. Use a `<button>` for actions such as opening a dialog or submitting an interaction.

## 6. Make the layout work on smaller screens

Our project grid has three columns on wider screens and one column below `800px`.

Try narrowing your browser window. The cards should stack vertically, giving their content more room.

The hero heading uses:

```css
font-size: clamp(2.5rem, 7vw, 4.5rem);
```

This lets the text scale with the viewport while keeping a minimum and maximum size.

Responsive design also means checking real content. Try a longer project title, increase your browser’s text size, and confirm that nothing overlaps.

## 7. Avoid a few beginner mistakes

**Define styled components outside your React component.** Keep declarations such as `const Card = styled.article` at the module level, as in our example. Creating them during rendering can cause unnecessary component recreation. The [styled-components FAQ](https://styled-components.com/docs/faqs#why-should-i-avoid-declaring-styled-components-in-the-render-method) explains the consequences.

**Keep keyboard focus visible.** Press Tab to move through your links. You should always be able to tell which element is selected.

**Watch for leftover CSS.** If the page looks unexpectedly centered or constrained, check for imports from the Vite starter styles.

**Start with a small component vocabulary.** Names like `Card`, `Navigation`, and `Footer` communicate their purpose clearly. You can split them into separate files when the project grows.

## 8. Build and personalize your website

When you’re ready, run:

```bash
npm run build
npm run preview
```

The build command creates the production files. The preview command lets you inspect that build locally; it isn’t a production hosting service. These commands are documented in the [Vite guide](https://vite.dev/guide/).

Now make the website yours: change the name, write your own introduction, and replace the sample projects. Add links when you have working demos to share.

You’ve practiced component styling, reusable layouts, conditional styles, and responsive CSS—all within one small React website.

What will you build next? ✨
