# Type Literal Tabs Anywhere

You press Tab and the cursor jumps to a different field. Or the shell starts autocompleting. Or your editor inserts four spaces. Meanwhile, the Makefile, TSV file, or `sed` pattern in front of you needs one specific character: `U+0009`, the horizontal tab.

Here is how to get a literal tab into almost any context.

## 1. The shell: quoted insert

In bash and zsh, Tab triggers completion. To bypass it, press **Ctrl+V**, then **Tab**. Readline calls this `quoted-insert`: the next keystroke is inserted literally instead of being interpreted.

```bash
echo "a<Ctrl+V><Tab>b"
```

This works for other control characters too. Ctrl+V followed by Esc inserts a literal escape character, which is handy for ANSI color codes.

If you'd rather not fight the keyboard, use the shell's own escapes:

```bash
printf 'a\tb\n'
echo $'a\tb'      # bash/zsh ANSI-C quoting
```

## 2. PowerShell

PSReadLine on Windows binds Ctrl+V to paste, so use an escape instead. Inside double quotes, a backtick-t is a tab:

```powershell
"name`tvalue"
[char]9            # the character itself
```

Single-quoted strings don't expand escapes, so `'a`tb'` stays literal. This catches people out regularly.

## 3. Vim and Neovim

Tab normally indents according to `expandtab`. In insert mode, **Ctrl+V Tab** inserts a real tab regardless of settings. On Windows gvim, where Ctrl+V may be paste, use **Ctrl+Q**.

To see what you've got:

```vim
:set list listchars=tab:→\ ,trail:·
```

Now tabs and trailing spaces are visible, which saves a lot of debugging.

## 4. VS Code and other editors

If the editor inserts spaces, you have two options:

- Set `"editor.insertSpaces": false` for the language you're in (per-language settings work well for Makefiles and Go).
- Use the command **Indent Using Tabs** from the Command Palette to convert the current file.

If Tab is moving focus instead of inserting a character, you've probably toggled accessibility mode. **Ctrl+M** switches "Tab moves focus" on and off in VS Code.

## 5. Browser text fields and chat apps

In a `<textarea>`, an input, or a chat box, Tab moves focus and there's no escape sequence. The universal workaround is to **copy a tab from somewhere else and paste it**.

You can generate one on demand:

```bash
printf '\t' | pbcopy                 # macOS
printf '\t' | xclip -selection c     # Linux
```
```powershell
"`t" | Set-Clipboard                 # Windows
```

Then Ctrl+V into the field. Some apps trim whitespace on paste, but most leave a lone tab alone.

If you build the text field yourself, you can intercept the key:

```js
textarea.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    e.preventDefault();
    document.execCommand('insertText', false, '\t');
  }
});
```

Be careful, though. Trapping Tab breaks keyboard navigation for people who rely on it. If you do this, offer a way out, such as pressing Esc and then Tab to leave the field, and document it.

## 6. When you just need to match a tab

Often you don't need to *type* a tab at all, only to match one:

```bash
grep -P '\t' file.txt           # PCRE
sed 's/\t/,/g' file.txt         # GNU sed
cut -f2 data.tsv                # tab is cut's default delimiter
```

BSD/macOS `sed` doesn't understand `\t` in the pattern, so use `$'\t'` from bash or zsh, or switch to `perl -pe`.

## Quick reference

| Context | How |
|---|---|
| bash / zsh prompt | Ctrl+V, Tab, or `$'\t'` |
| PowerShell | `` `t `` in double quotes, or `[char]9` |
| Vim | Ctrl+V Tab (Ctrl+Q on Windows) |
| VS Code | `insertSpaces: false`, or Ctrl+M to stop focus-moving |
| Browser or chat | Paste a tab from the clipboard |

## Wrapping up

Every one of these tricks is the same idea: tell the program "treat the next thing literally." Once you know that Ctrl+V is usually the "literal next" key and that most shells have a `\t` escape, a stubborn Tab key is rarely a problem.

What's your favorite way to deal with tabs? Tell me in the comments.
