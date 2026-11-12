test: Add new ChainTestingSetup and use it

Previously, tests that wanted to exercise ChainstateManager behaviour
directly (most notably validation_chainstatemanager_tests) had to pick
between BasicTestingSetup and TestingSetup. Neither fit well.

BasicTestingSetup does too little: it does not set up the scheduler,
the block tree database, the mempool, or the other pieces of global
state that chainstate code expects. Tests built on it end up
recreating that setup by hand, or quietly relying on state left over
from other tests.

TestingSetup does too much: it fully initializes g_chainman, loads the
genesis block and activates the best chain. A test that then creates
its own ChainstateManager has two managers sharing the same global
block index and block tree database. That happens to work for the
operations covered today, but it is fragile and makes it hard to
reason about which manager a given validation function is acting on,
since many of those functions still reach for g_chainman implicitly.

Introduce ChainTestingSetup, which performs every step of TestingSetup
up to, but not including, initialization of the chainstate itself:
it starts the scheduler and validation interface queue, creates the
block tree database, sets up the mempool, and populates the
NodeContext. TestingSetup now derives from ChainTestingSetup and adds
only the chainstate initialization, genesis block loading and
ActivateBestChain, so its behaviour is unchanged for existing users.

Switch the tests that construct their own ChainstateManager, or that
otherwise do not need an activated chain, to ChainTestingSetup. This
removes the duplicate manager problem and makes each test's
dependencies on global state explicit.

This is also a step towards removing the g_chainman global, because
tests can now own and pass around their ChainstateManager instance
instead of depending on the global one.
