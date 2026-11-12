# Tips for Organizing React Projects

A React project starts small. You have a few components, a `App.jsx`, and maybe a `utils.js` file. Then features pile up, teammates join, and suddenly finding anything takes longer than writing it. Good organization doesn't prevent growth problems entirely, but it makes them much easier to manage. Here are some practical tips that have helped me keep projects maintainable.

## 1. Organize by feature, not by file type

It's tempting to group files by type: all components in one folder, all hooks in another, all styles in a third. This works for tiny apps, but it scatters related code across the tree. A feature like "cart" ends up touching five different directories.

A feature-based layout keeps related code together:

```
src/
  features/
    cart/
      CartPage.jsx
      CartItem.jsx
      useCart.js
      cartSlice.js
      cart.test.jsx
    auth/
      LoginForm.jsx
      useAuth.js
      authApi.js
  shared/
    components/
      Button.jsx
      Modal.jsx
    hooks/
      useDebounce.js
  App.jsx
  main.jsx
```

When you need to change how the cart works, everything lives in one place. Deleting a feature becomes a single folder removal instead of a hunt through the codebase.

## 2. Keep a clear boundary for shared code

Not everything belongs to a feature. Buttons, modals, formatters, and generic hooks get reused across the app. Put these in a `shared/` (or `common/`) folder, and be strict about what goes there. A useful rule: code moves into `shared/` only when it's used by two or more features. Premature sharing creates coupling that's painful to undo.

## 3. Use an index file sparingly

Barrel files (`index.js` files that re-export everything in a folder) make imports tidy, but they can hurt build performance and make circular dependencies harder to spot. If you use them, keep them at the feature boundary, not on every folder, and check your bundle output occasionally.

## 4. Separate UI from logic

Components that fetch data, manage state, and render markup all at once become hard to test and reuse. A common pattern is to move logic into custom hooks:

```jsx
// useCart.js
export function useCart() {
  const [items, setItems] = useState([]);
  const total = items.reduce((sum, item) => sum + item.price, 0);
  // ...add, remove, clear
  return { items, total, addItem, removeItem };
}
```

```jsx
// CartPage.jsx
export function CartPage() {
  const { items, total } = useCart();
  return <CartView items={items} total={total} />;
}
```

`CartView` is now a pure presentational component you can test or render in Storybook without mocking anything.

## 5. Centralize API calls

Scattering `fetch` calls throughout components makes changes painful. Create a single API layer per feature (like `authApi.js` above) or one shared client that handles base URLs, headers, and error normalization. When the backend changes, you update one file.

## 6. Pick naming conventions and stick to them

Decide on conventions early and write them down:

- **Components:** `PascalCase.jsx`
- **Hooks:** `useSomething.js`
- **Utilities:** `camelCase.js`
- **Tests:** colocate them next to the file they test (`Button.test.jsx`)

Enforce these with a linter or a pre-commit hook rather than relying on code review alone.

## 7. Don't over-abstract early

Folder structure is easy to change later, but over-engineered abstractions are harder to unwind. Start with the simplest structure that works, and reorganize when real pain shows up. If you find yourself adding three layers of indirection for a form with two fields, step back.

## 8. Document the structure

A short `README` section or an `ARCHITECTURE.md` explaining your folder conventions saves new teammates hours. Include a few sentences on where new features should go and what belongs in `shared/`.

## Wrapping up

There's no single correct structure for every React project. The best layout is one your team understands and applies consistently. Start with features as your primary organizing unit, keep shared code deliberate, separate logic from presentation, and document your choices. Your future self will thank you.

What organization patterns have worked for you? Share them in the comments below!
