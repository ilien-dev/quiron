# A React website with Styled-components for beginners ✨

React makes it easy to split a website into reusable components, but every component still needs styling. You could use regular CSS files, CSS Modules, or a utility framework. Another beginner-friendly option is **styled-components**, a library that lets you write CSS directly inside your JavaScript files.

In this tutorial, we’ll build a small React landing page with a navigation bar, hero section, feature cards, and footer. Along the way, you’ll learn how to create styled components, pass props to them, reuse styles, add responsive behavior, and use a theme.

## What is styled-components?

Styled-components is a CSS-in-JS library. Instead of creating a CSS class and attaching it to an HTML element, you create a React component that already includes its styles.

With regular CSS, you might write:

```css
.button {
  padding: 12px 20px;
  background: purple;
  color: white;
}
```

Then use it like this:

```jsx
<button className="button">Get started</button>
```

With styled-components, the same button becomes:

```jsx
const Button = styled.button`
  padding: 12px 20px;
  background: purple;
  color: white;
`;
```

You can use `Button` just like any other React component:

```jsx
<Button>Get started</Button>
```

Styled-components generates unique class names behind the scenes, so you don’t have to worry about accidentally reusing a class name elsewhere.

## Creating the project

We’ll use Vite to create our React project. Run the following commands in your terminal:

```bash
npm create vite@latest styled-website -- --template react
cd styled-website
npm install
npm install styled-components
npm run dev
```

Open the local URL shown in your terminal. You should see the default Vite page.

Now replace the contents of `src/App.jsx`. We’ll build the page step by step, but the final application will remain in this single file so it’s easy to follow.

Start by importing `styled`:

```jsx
import styled from "styled-components";
```

The `styled` object gives us helpers such as `styled.div`, `styled.button`, and `styled.header`. Each helper creates a styled React component.

## Adding the page container

Let’s create a wrapper for the entire page:

```jsx
const Page = styled.div`
  min-height: 100vh;
  background: #f8f7fc;
  color: #252238;
  font-family: Inter, system-ui, sans-serif;
`;
```

The text between the backticks is regular CSS. This syntax is called a **tagged template literal**, but you don’t need to understand its internal details to use it.

Add the component to `App`:

```jsx
function App() {
  return <Page>Hello, styled-components!</Page>;
}

export default App;
```

The important naming convention is that styled components begin with a capital letter. React treats lowercase names as HTML elements and uppercase names as custom components.

## Building the navigation bar

Next, create the styled components for our navigation:

```jsx
const Header = styled.header`
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.a`
  color: #6c4ee3;
  font-size: 1.4rem;
  font-weight: 800;
  text-decoration: none;
`;

const Nav = styled.nav`
  display: flex;
  align-items: center;
  gap: 24px;
`;

const NavLink = styled.a`
  color: #59556b;
  font-weight: 600;
  text-decoration: none;

  &:hover {
    color: #6c4ee3;
  }
`;
```

Notice the `&:hover` rule inside `NavLink`. The ampersand represents the generated element, so this works like a normal CSS hover selector.

Now update `App`:

```jsx
function App() {
  return (
    <Page>
      <Header>
        <Logo href="#">Brightly ✨</Logo>

        <Nav>
          <NavLink href="#features">Features</NavLink>
          <NavLink href="#about">About</NavLink>
        </Nav>
      </Header>
    </Page>
  );
}
```

Our styled components still support normal HTML attributes. Because `Logo` and `NavLink` are based on anchor elements, we can give them an `href`.

## Creating a reusable button

Buttons are perfect examples of reusable components. Let’s create one with two visual variants:

```jsx
const Button = styled.a`
  display: inline-block;
  padding: 13px 22px;
  border: 2px solid #6c4ee3;
  border-radius: 10px;
  background: ${({ $secondary }) =>
    $secondary ? "transparent" : "#6c4ee3"};
  color: ${({ $secondary }) =>
    $secondary ? "#6c4ee3" : "#ffffff"};
  font-weight: 700;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(108, 78, 227, 0.2);
  }
`;
```

Styled-components can read props inside the CSS. Here, `$secondary` changes the background and text color.

Props beginning with `$` are called **transient props**. Styled-components uses them while styling but does not add them to the resulting HTML element. This keeps the browser console clean.

These buttons will now have different appearances:

```jsx
<Button href="#features">Explore features</Button>
<Button href="#about" $secondary>
  Learn more
</Button>
```

## Designing the hero section

The hero section introduces the website and gives visitors a clear action to take.

```jsx
const Hero = styled.main`
  max-width: 1100px;
  margin: 0 auto;
  padding: 90px 24px 110px;
  text-align: center;
`;

const Badge = styled.span`
  display: inline-block;
  margin-bottom: 20px;
  padding: 8px 14px;
  border-radius: 999px;
  background: #ebe6ff;
  color: #6c4ee3;
  font-size: 0.9rem;
  font-weight: 700;
`;

const Title = styled.h1`
  max-width: 800px;
  margin: 0 auto;
  font-size: clamp(2.5rem, 7vw, 5rem);
  line-height: 1.05;
  letter-spacing: -0.05em;
`;

const Highlight = styled.span`
  color: #6c4ee3;
`;

const Description = styled.p`
  max-width: 650px;
  margin: 24px auto 32px;
  color: #686477;
  font-size: 1.15rem;
  line-height: 1.7;
`;

const Actions = styled.div`
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
`;
```

Now add the hero below `Header`:

```jsx
<Hero>
  <Badge>Made for curious developers</Badge>

  <Title>
    Build delightful websites with <Highlight>confidence</Highlight>
  </Title>

  <Description>
    A simple place to learn, experiment, and turn your ideas into
    polished web experiences.
  </Description>

  <Actions>
    <Button href="#features">Explore features</Button>
    <Button href="#about" $secondary>
      Learn more
    </Button>
  </Actions>
</Hero>
```

The `clamp()` function makes the title responsive. It uses a flexible size based on the viewport while staying between a minimum of `2.5rem` and a maximum of `5rem`.

## Adding feature cards

Create a section and a reusable card component:

```jsx
const FeaturesSection = styled.section`
  padding: 80px 24px;
  background: #ffffff;
`;

const SectionTitle = styled.h2`
  margin: 0 0 48px;
  text-align: center;
  font-size: 2.2rem;
`;

const FeatureGrid = styled.div`
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;

  @media (max-width: 760px) {
    grid-template-columns: 1fr;
  }
`;

const Card = styled.article`
  padding: 28px;
  border: 1px solid #e8e5f1;
  border-radius: 18px;
  background: #ffffff;
  box-shadow: 0 12px 30px rgba(37, 34, 56, 0.06);
`;

const Icon = styled.div`
  margin-bottom: 18px;
  font-size: 2rem;
`;

const CardTitle = styled.h3`
  margin: 0 0 10px;
`;

const CardText = styled.p`
  margin: 0;
  color: #686477;
  line-height: 1.65;
`;
```

The media query changes the three-column grid into one column on smaller screens. Because it lives inside `FeatureGrid`, it only affects that component.

Add the feature section after `Hero`:

```jsx
<FeaturesSection id="features">
  <SectionTitle>Everything you need to begin</SectionTitle>

  <FeatureGrid>
    <Card>
      <Icon>🎨</Icon>
      <CardTitle>Flexible styling</CardTitle>
      <CardText>
        Write familiar CSS while keeping each component’s styles close
        to its markup.
      </CardText>
    </Card>

    <Card>
      <Icon>🧩</Icon>
      <CardTitle>Reusable components</CardTitle>
      <CardText>
        Create building blocks that can be shared throughout your
        application.
      </CardText>
    </Card>

    <Card>
      <Icon>📱</Icon>
      <CardTitle>Responsive layouts</CardTitle>
      <CardText>
        Add media queries directly to components and adapt them for any
        screen size.
      </CardText>
    </Card>
  </FeatureGrid>
</FeaturesSection>
```

This works, but the three cards repeat the same structure. In a larger application, it’s cleaner to store the content in an array and render it with `map()`:

```jsx
const features = [
  {
    icon: "🎨",
    title: "Flexible styling",
    text: "Write familiar CSS while keeping styles close to the markup.",
  },
  {
    icon: "🧩",
    title: "Reusable components",
    text: "Create building blocks that can be shared across your app.",
  },
  {
    icon: "📱",
    title: "Responsive layouts",
    text: "Adapt components for phones, tablets, and desktops.",
  },
];
```

Then replace the individual cards with:

```jsx
<FeatureGrid>
  {features.map((feature) => (
    <Card key={feature.title}>
      <Icon>{feature.icon}</Icon>
      <CardTitle>{feature.title}</CardTitle>
      <CardText>{feature.text}</CardText>
    </Card>
  ))}
</FeatureGrid>
```

## Extending an existing component

Sometimes two elements need mostly the same styles. Instead of copying everything, you can extend an existing styled component.

For example, let’s create a darker call-to-action section based on `FeaturesSection`:

```jsx
const CallToAction = styled(FeaturesSection)`
  background: #252238;
  color: #ffffff;
  text-align: center;
`;

const CallToActionText = styled.p`
  max-width: 560px;
  margin: -28px auto 30px;
  color: #c9c5d8;
  line-height: 1.7;
`;
```

Use it below the features:

```jsx
<CallToAction id="about">
  <SectionTitle>Ready to build something?</SectionTitle>

  <CallToActionText>
    Start with one component, style it, and keep improving your page
    one small step at a time.
  </CallToActionText>

  <Button href="#">Start building</Button>
</CallToAction>
```

`CallToAction` receives all the styles from `FeaturesSection`, and then overrides the background while adding its own styles.

## Adding global styles

Our page still has the browser’s default body margin. Styled-components provides `createGlobalStyle` for styles that apply to the whole document.

Update the import:

```jsx
import styled, { createGlobalStyle } from "styled-components";
```

Create the global styles:

```jsx
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }

  html {
    scroll-behavior: smooth;
  }

  body {
    margin: 0;
  }

  button,
  a {
    font: inherit;
  }
`;
```

Render `GlobalStyle` near the top of `App`:

```jsx
function App() {
  return (
    <>
      <GlobalStyle />
      <Page>
        {/* The rest of the website */}
      </Page>
    </>
  );
}
```

Unlike our other components, `GlobalStyle` does not display an element. It inserts the global CSS rules into the page.

## Using a theme

As your application grows, repeating color values becomes difficult to maintain. A theme lets you keep shared design values in one object.

Import `ThemeProvider`:

```jsx
import styled, {
  createGlobalStyle,
  ThemeProvider,
} from "styled-components";
```

Create a theme:

```jsx
const theme = {
  colors: {
    primary: "#6c4ee3",
    text: "#252238",
    muted: "#686477",
    surface: "#ffffff",
    background: "#f8f7fc",
  },
};
```

Wrap the page with the provider:

```jsx
function App() {
  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Page>{/* Website content */}</Page>
    </ThemeProvider>
  );
}
```

Every styled component can now access the theme:

```jsx
const Logo = styled.a`
  color: ${({ theme }) => theme.colors.primary};
  font-size: 1.4rem;
  font-weight: 800;
  text-decoration: none;
`;
```

You can gradually replace the hard-coded colors in the other components. If you later change the primary color in the theme, every component using it will update automatically.

## A few beginner tips

Styled-components becomes easier once you follow a few simple habits:

- Give components meaningful names such as `FeatureGrid` instead of `StyledDiv`.
- Keep small styled components near the React component that uses them.
- Move shared components, such as buttons, into their own files as the project grows.
- Use transient props like `$secondary` for styling-only values.
- Store repeated colors, spacing, and breakpoints in a theme.
- Avoid creating styled components inside your component function, because they would be recreated after every render.

Styled-components does not replace CSS knowledge. Properties, selectors, Flexbox, Grid, pseudo-classes, and media queries still work the same way. The library simply gives you a component-focused way to organize them.

## Final thoughts

You now have a responsive React landing page built from styled components. We created reusable elements, changed styles with props, added hover states and media queries, extended an existing component, applied global styles, and introduced a shared theme.

The biggest advantage is how naturally styling fits into React’s component model. A button can contain its appearance, variants, and interaction states in one reusable unit. A page can then be assembled from those units without managing a growing collection of global class names.

Start small. Style one component, reuse it somewhere else, and extract shared values only when repetition appears. Before long, you’ll have your own tiny design system—and a polished React website to go with it. ✨