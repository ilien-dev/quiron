# A React website with Styled-components for beginners ✨

This is week three of me learning React, and I wanted to build a website from scratch, but I was torn between CSS modules and styled-components. Then I watched a YouTube tutorial on styled-components and how it uses props, and that settled it. 😁

So I built a simple practice site called Home Made, based on the concept of a healthy meal kit service. My workflow was Figma wireframes first, then the design, then the code. All of the code is available on GitHub: [Home-made-React](https://github.com/muchirijane/Home-made-React). Not all of it is included in this post, because it would be way too long.

## What is styled-components?

[Styled-components](https://styled-components.com/) is a CSS-in-JS library. Instead of creating a CSS class and attaching it to an HTML element, you create a React component that already has its styles.

With regular CSS, you might write:

```css
.button {
  padding: 12px 20px;
  background: purple;
  color: white;
}
```

and then use it like this:

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

and you use `Button` like any other React component. Styled-components generates unique class names behind the scenes, so you don't have to worry about reusing a class name somewhere else by accident.

## Props for button variants

This is the part I liked most. My buttons come in two variations, where the primary one is orange (`#E38B06`) and the other one is black, and instead of writing two separate components you pass a prop and read it inside the CSS. Here's the idea with a `$secondary` prop:

```jsx
const Button = styled.a`
  background: ${({ $secondary }) =>
    $secondary ? "black" : "#E38B06"};
  color: #ffffff;
`;
```

```jsx
<Button href="#">Get started</Button>
<Button href="#" $secondary>Get started</Button>
```

## Things I had to google

I had to google how to set up global styles, how to import a font and how to import local images. Googling is a real skill, and honestly none of that time felt wasted.

For global styles, styled-components has `createGlobalStyle`. The docs for it and the [Styled-components Spectrum community](https://spectrum.chat/styled-components?tab=posts) helped me a lot. My font is Nunito.

```jsx
import styled, { createGlobalStyle } from "styled-components";

const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
  }
`;
```

You render `<GlobalStyle />` near the top of `App`. It doesn't display an element on the page; the CSS rules are just inserted into the document.

## The navbar took forever

The navbar took way longer than I expected, especially the click functionality to open and close the menu. I used `react-router-dom`, `react-icons` (the Boxicons set), `useState` for the toggle and `IconContext.Provider`.

If you forget to wrap your app in a Router, you'll get this error:

```
Invariant failed: You should not use <Link> outside a <Router>
```

I also didn't position things from memory. Everything was placed by inspecting the page in Chrome dev tools until it sat where I wanted it.

## The sections

The site has a navbar, a hero, a "how it works" section with 3 cards, a welcome section, recipes, a section about personalizing your meals, and a footer. The idea for the recipes section came from Dribbble, and making it responsive was painful, so that code is the worst in the whole project. It hurts my eyes. 🙈

I used mostly flexbox, although grid would have been easier for some of these layouts. Also, I'm bad at naming folders.

One trick that helped me: look at the layout as big blocks inside other blocks, like the Pesticide Chrome extension does.

Here are the styles for some of the components:

- [gist 1](https://gist.github.com/muchirijane/d34e08fb862862c3bc674930e16052e1)
- [gist 2](https://gist.github.com/muchirijane/bfb2d4f390c2eb84a2c16350e61e240a)
- [gist 3](https://gist.github.com/muchirijane/80b39f5bf728868fe284c8f750c57c59)
- [gist 4](https://gist.github.com/muchirijane/0b6abe7560af665a4207f153b9509aac)
- [gist 5](https://gist.github.com/muchirijane/7e9558564ed00ba80982df3a77c5d5a9)
- [gist 6](https://gist.github.com/muchirijane/3d8eb92ab4b6c6141a4603a43ba931d3)

## VS Code extensions

Two extensions I'd suggest if you're starting out: [vscode-styled-components](https://marketplace.visualstudio.com/items?itemName=jpoissonnier.vscode-styled-components) and [es7-react-js-snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets).

## What's next

I still need to refactor and clean up the code, and after that I want to build another website where the content comes from a data file and is rendered with the map method.

I'm pretty sure I'll laugh at this code in 5 years, and that's fine.

If this helped you, you can [buy me a coffee](https://www.buymeacoffee.com/janetracy). ☕
