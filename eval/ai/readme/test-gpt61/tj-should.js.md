# should.js

> BDD style assertions for node.js — test framework agnostic.

should.js is an assertion library for Node.js that helps you write tests in the language of expected behavior. Its fluent interface makes assertions read like sentences, keeping the intent of a test close to the code that expresses it.

```js
const should = require('should');

const user = {
  name: 'Ada',
  active: true,
  roles: ['reader', 'editor']
};

user.name.should.equal('Ada');
user.active.should.be.true();
user.roles.should.containEql('editor');

should(user).have.property('name', 'Ada');
```

Use should.js with your preferred test framework, a small verification script, or any environment that reports thrown assertion errors. It supplies the assertions; you choose how to organize and run your tests.

## Why should.js?

Good tests explain what matters. An assertion should make the expected outcome clear without forcing readers to decode a complicated expression.

With should.js, you can describe values, object properties, collections, and errors directly:

```js
response.should.have.property('status', 200);
response.body.should.be.an.Object();
response.body.items.should.have.length(3);
```

The library provides:

- **Readable assertions:** express expectations through a chainable API.
- **Framework independence:** use the same assertion style across different test runners.
- **Deep comparisons:** check nested objects and arrays by their contents.
- **Useful failure information:** inspect assertion errors when behavior differs from expectations.
- **Two entry styles:** use a value’s `.should` property or call `should(value)` explicitly.

Assertions are executable expectations. When an expectation holds, execution continues. When it fails, should.js throws an assertion error that your test runner can report.

## Installation

Add should.js as a development dependency:

```sh
npm install --save-dev should
```

Load it in your test file:

```js
const should = require('should');
```

Requiring `should` makes the fluent `.should` interface available on ordinary values. The exported function also lets you assert against values explicitly:

```js
'hello'.should.be.a.String();

should('hello').be.a.String();
```

Both forms express the same expectation. Choose the style that best fits your project, and use it consistently.

## Your first test

Here is a complete example using Node.js’s built-in test runner:

```js
const { test } = require('node:test');
const should = require('should');

function add(a, b) {
  return a + b;
}

test('adds two numbers', () => {
  add(2, 3).should.equal(5);
});
```

Save the file as `test/add.test.js`, then run:

```sh
node --test
```

should.js does not define test cases, discover files, or manage test execution. Those responsibilities belong to the runner. This separation lets you adopt its assertion style without changing how your test suite is organized.

## Core assertions

### Equality

Use `.equal()` when you expect strict equality:

```js
const answer = 42;

answer.should.equal(42);
answer.should.not.equal('42');
```

Strict equality compares objects by identity. Two separately created objects are different values, even when their properties match.

Use `.eql()` to compare their contents:

```js
const actual = {
  name: 'Ada',
  preferences: {
    theme: 'dark'
  }
};

actual.should.eql({
  name: 'Ada',
  preferences: {
    theme: 'dark'
  }
});
```

Deep equality is especially useful for returned data, configuration objects, and transformed collections.

### Types and booleans

State the type or exact boolean value you expect:

```js
'hello'.should.be.a.String();
(42).should.be.a.Number();
[1, 2, 3].should.be.an.Array();
({}).should.be.an.Object();

true.should.be.true();
false.should.be.false();
```

Prefer an exact boolean assertion when the distinction matters. A function that promises to return `true` should not silently satisfy a test by returning some other truthy value.

### Numbers

Express bounds directly:

```js
const score = 85;

score.should.be.above(80);
score.should.be.below(100);
score.should.be.within(0, 100);
```

For floating-point calculations, use an appropriate tolerance:

```js
const total = 0.1 + 0.2;

total.should.be.approximately(0.3, 0.000001);
```

This communicates the precision your application requires while accounting for floating-point arithmetic.

### Strings

Check exact values, patterns, or meaningful boundaries:

```js
const message = 'Hello, Ada!';

message.should.equal('Hello, Ada!');
message.should.startWith('Hello');
message.should.endWith('!');
message.should.match(/Ada/);
```

Choose the narrowest assertion that captures the requirement. If only a prefix is part of the contract, asserting the entire string can make a test unnecessarily fragile.

## Objects and collections

Property assertions help describe an object’s public shape:

```js
const user = {
  id: 7,
  name: 'Ada',
  active: true
};

user.should.have.property('id', 7);
user.should.have.properties(['name', 'active']);
```

A property assertion can also move the chain to the property’s value:

```js
user.should.have.property('name').which.is.a.String();
```

For arrays, assert the expected length or the presence of an element:

```js
const tags = ['node', 'testing', 'bdd'];

tags.should.have.length(3);
tags.should.containEql('testing');
```

Use deep equality when the whole collection, including its order, matters:

```js
tags.should.eql(['node', 'testing', 'bdd']);
```

For collections of objects, `.containEql()` checks for an element with matching contents:

```js
const users = [
  { id: 1, name: 'Ada' },
  { id: 2, name: 'Grace' }
];

users.should.containEql({ id: 2, name: 'Grace' });
```

These assertions let you distinguish between “this result contains the item I need” and “this result matches every expected item exactly.”

## Null and undefined

`null` and `undefined` cannot expose a `.should` property. Use the exported function when testing either value:

```js
should(null).be.null();
should(undefined).be.undefined();
```

The function form is also convenient whenever a value might be absent:

```js
const result = findUser();

should(result).not.be.undefined();
```

An explicit existence assertion makes the expectation clear before subsequent assertions inspect the result.

## Errors

To test a synchronous exception, wrap the operation in a function:

```js
function parseConfiguration() {
  throw new Error('Invalid configuration');
}

(() => {
  parseConfiguration();
}).should.throw('Invalid configuration');
```

The wrapper lets should.js invoke the operation and inspect the error. Calling the operation before constructing the assertion would throw too early.

You can also check an error type:

```js
(() => {
  throw new TypeError('Expected a string');
}).should.throw(TypeError);
```

Assert the error details that callers depend on. Checking incidental wording can create maintenance work without protecting meaningful behavior.

## Asynchronous tests

Use your runner’s support for promises or `async` functions, then assert against the resolved result:

```js
const { test } = require('node:test');
const should = require('should');

async function loadUser() {
  return { id: 7, name: 'Ada' };
}

test('loads a user', async () => {
  const user = await loadUser();

  user.should.have.property('id', 7);
  user.should.have.property('name', 'Ada');
});
```

Always return or await asynchronous work so the runner knows when the test is complete. An assertion that runs after a test has finished cannot reliably validate that test.

## Writing maintainable assertions

Start with the behavior a caller should observe. Give each test a descriptive name, arrange representative input, perform the operation, and assert the relevant result.

Keep assertion chains short enough to read comfortably. Separate assertions often explain independent expectations more clearly than one long chain.

Use exact comparisons for stable contracts and focused assertions for partial requirements. For example, checking one required property allows unrelated properties to evolve, while deep equality deliberately fixes the complete expected structure.

Finally, let failures guide improvements. When a failed test is difficult to understand, simplify its setup or make its expectations more explicit. The best assertions help the next reader understand both what happened and what should have happened.
