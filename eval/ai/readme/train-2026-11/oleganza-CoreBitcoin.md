I wrote `README.md`; it comes to 812 words, close to your 808 target.

It covers:
- **Intro:** the "Awesome Bitcoin toolkit for ObjC and Swift" tagline and a short description.
- **Why CoreBitcoin?** The design goals: readable code, safe defaults, no hidden network calls, a native Cocoa feel.
- **Features:** keys and addresses, BIP32/BIP39 wallets, transactions and scripts, encoding and hashing, payments and currency formatting, and blocks.
- **Installation:** CocoaPods and prebuilt frameworks.
- **Quick start:** Objective-C and Swift examples, plus building a transaction.
- **Testing, security notes, contributing and license.**

Check these against the actual codebase before publishing, because I wrote them without looking at the code:
- Class and method names (e.g. `BTCTransactionBuilder`, `BTCScriptMachine`, `derivedKeychainWithPath:`).
- The build script names (`update_openssl.sh`, `build_libraries.sh`) and the `xcodebuild` scheme name.
- Platform support (iOS/macOS/tvOS/watchOS) and the BIP70 claim.
- The WTFPL license.
