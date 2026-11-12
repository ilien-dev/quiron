### What does this PR change?

This PR makes `schema-registry.subject` optional when using the `avro-confluent` format with Kafka and upsert-Kafka sinks.

Previously, users had to specify a Schema Registry subject for each Avro key or value, even when following the conventional topic-based naming scheme. For example, a sink writing to `orders` needed an explicit `orders-value` subject for its value format.

When the option is omitted, the connector now derives the subject from the sink topic:

- `<topic_name>-key` for the key format
- `<topic_name>-value` for the value format

An explicitly configured subject continues to take precedence, so existing configurations and custom subject names remain supported. The Schema Registry URL is still required. For sinks using other connectors, such as filesystem, the subject must still be configured explicitly because those connectors do not supply a Kafka topic name.

This reduces configuration for common Kafka setups and aligns the default subject names with the Kafka and Confluent ecosystem. It also allows key and value formats to use their respective defaults independently.

The format documentation describes the defaults and the requirement for other connectors. See [FLINK-20348](https://issues.apache.org/jira/browse/FLINK-20348) and the [Flink 1.13 Confluent Avro documentation](https://nightlies.apache.org/flink/flink-docs-release-1.13/docs/connectors/table/formats/avro-confluent/).
