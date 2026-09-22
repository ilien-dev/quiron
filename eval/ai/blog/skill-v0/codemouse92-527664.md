# Type literal tabs anywhere

Tabs versus spaces is one of those debates that never seems to end. Today I want to talk about something a little different, though: a small productivity trick that lets you type literal tab characters anywhere, even in places where your editor or browser tries to "help" by moving focus instead.

## The problem

If you've ever tried to press Tab inside a text field (a `<textarea>`, a code editor widget embedded in a web page, or even some desktop apps), you've probably noticed that focus jumps to the next element on the page. No tab character gets inserted. That's expected behavior in most contexts, and accessibility depends on it! It becomes a real annoyance, though, when you're trying to write code or format a table, or you otherwise need an actual tab character in your text.

It happens most often with:

- Plain `<textarea>` elements on websites
- Online code playgrounds without special tab handling
- Certain terminal emulators
- Some lightweight text editors

## Why this happens

By default, the Tab key is reserved by browsers and operating systems for navigation. It's part of what makes the web (and software in general) accessible. Keyboard users rely on Tab to move between interactive elements without needing a mouse. If every text field captured Tab and turned it into a literal character, keyboard navigation would break down completely.

So this is a deliberate default, and calling it a "bug" would be unfair. It does mean that if you specifically want a tab character, you need a workaround.

## The fix: a Unicode tab character

One simple trick is to copy and paste a literal tab character straight into your text. You can grab one from here if you need it:

```
	
```

The whitespace between the backticks above is an actual tab character. Copy it and you can paste it anywhere, into a textarea, a form field or a chat box, and it'll insert a real tab instead of shifting focus.

I know it sounds almost too simple. I still find it useful when I'm stuck in an environment that doesn't give me native tab support.

## A better fix: JavaScript for your own projects

If you're building your own web app and want a `<textarea>` to properly support tab characters (a common ask for anything code-related), you can intercept the keydown event and insert the tab character yourself:

```js
textarea.addEventListener('keydown', function (e) {
  if (e.key === 'Tab') {
    e.preventDefault();

    const start = this.selectionStart;
    const end = this.selectionEnd;

    this.value =
      this.value.substring(0, start) + '\t' + this.value.substring(end);

    this.selectionStart = this.selectionEnd = start + 1;
  }
});
```

This listens for the Tab key and prevents the default focus-shifting behavior. Then it inserts a tab character at the cursor position and moves the cursor to just after it.

Keep in mind that this takes keyboard-based tab navigation away from that field. Only do it where that trade-off makes sense, like a code editor component. A general form is the wrong place for it.

## Editor-specific tricks

Some tools have their own built-in ways around this behavior:

- VS Code: Tab works natively for indentation inside the editor, so you don't need any tricks.
- CodePen and JSFiddle: many embedded editors already handle Tab properly for code indentation.
- Plain HTML forms: if you're stuck with a vanilla `<textarea>` and can't modify the JS, the copy-paste trick above is your best bet.

## When you just need a quick workaround

If you don't want to mess with JavaScript and just need to get a tab character into a form field right now, this is the fastest path I know:

1. Open a plain text editor (Notepad, TextEdit, whatever you have)
2. Type an actual Tab character there, since most plain text editors treat Tab as literal whitespace
3. Copy and paste it into the field you need

It's clunky. It also works everywhere, every time.

## Wrapping up

You won't need to type a literal tab character in places designed to intercept it very often. When you do, it can be surprisingly frustrating to figure out. You can grab a pre-made tab character, write your own JS handler, or bounce the tab off a plain text editor, and now you know how to do all three.

It's a small trick, but I think it's a handy one to keep in your back pocket.
