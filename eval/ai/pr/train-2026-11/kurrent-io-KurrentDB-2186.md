Draft based on the title; the PR diff wasn’t available to verify implementation details.

This PR stops persisting command and response messages, removing durable storage from the exchange used to coordinate requests and their results. Commands express work to perform, and responses report the outcome of that work. Keeping both as persisted records adds storage activity to the request lifecycle and retains messages whose usefulness is tied to an individual interaction.

The intended behavior is for commands and responses to pass through the messaging flow without being appended to persistent storage. A command should still reach its handler, and the resulting response should still reach the component waiting for it. Completing that exchange should no longer depend on writing either message to disk.

This change draws a clearer boundary between communication and durable state. Data required to represent a completed operation or recover its state should continue to follow the appropriate persistence path. The command that initiated an operation and the response returned to its caller should not acquire durability simply because they participate in that operation.

The expected benefit is fewer writes associated with internal coordination, along with less retained message data. Removing those writes should also simplify the lifecycle of command and response handling by eliminating persistence work that does not contribute to the durable result. Any performance improvement should be assessed through measurement; this description does not claim a specific throughput or latency gain.

Review should focus on the points where message delivery previously depended on persistence completing. Those transitions need to preserve ordering, correlation, error propagation, and completion behavior. Particular attention should go to failed operations, delayed responses, and shutdown while requests are in progress, since those cases can expose assumptions about a message having been stored.

Validation should cover successful command handling, delivery of the corresponding response, and failure handling without persisted command or response records. It should also confirm that operations requiring durable state still persist that state correctly. Restart behavior deserves explicit coverage wherever recovery previously consulted these messages. Test execution and compatibility details should be added from the implementation and CI results before merging, including whether existing stored messages require any handling during upgrade.
