# conversational-datasets

Large datasets for conversational AI.

`conversational-datasets` is a project for organizing, exploring, and preparing conversation data for research and development. It brings together the practical steps involved in working with dialogue at scale: understanding where data came from, inspecting its structure, selecting useful subsets, and preparing examples for downstream tasks.

Conversational AI depends on more than a large number of messages. Useful datasets need clear conversation boundaries, consistent roles, documented provenance, and an understanding of how the data may—and may not—be used. This project provides a starting point for that work.

## Who is this for?

This project is intended for people working with conversational data, including:

- Researchers studying dialogue, language models, and human–computer interaction.
- Engineers preparing training or evaluation data for conversational systems.
- Dataset curators documenting, cleaning, and maintaining collections.
- Practitioners exploring how conversation structure affects model behavior.

You can use the ideas and formats described here with public datasets, organization-owned data, or collections assembled for a specific research task. Check each dataset’s license and usage terms before downloading, modifying, or redistributing it.

## What is conversational data?

A conversational dataset typically contains a collection of conversations. Each conversation contains an ordered sequence of messages, often with a role identifying the speaker and optional metadata describing the context.

A minimal conversation might look like this:

```json
{
  "conversation_id": "example-001",
  "messages": [
    {
      "role": "user",
      "content": "How can I keep herbs fresh?"
    },
    {
      "role": "assistant",
      "content": "Trim the stems and place them in a jar of water."
    },
    {
      "role": "user",
      "content": "Should I refrigerate them?"
    },
    {
      "role": "assistant",
      "content": "It depends on the herb. Parsley and cilantro usually keep well in the refrigerator."
    }
  ],
  "metadata": {
    "language": "en",
    "source": "illustrative-example"
  }
}
```

This example is illustrative; individual datasets may use different field names and structures. Some include timestamps, conversation titles, tool calls, annotations, ratings, or multiple candidate responses. Others contain only text and speaker labels.

Preserving message order and conversation boundaries is essential. Flattening all messages into a single list can remove the context that makes a response meaningful.

## Getting started

Start by choosing a dataset that fits your task and checking its documentation. Before using the data, establish:

1. **Source and permission:** Where did the conversations come from, and what uses are permitted?
2. **Structure:** How are conversations, messages, roles, and metadata represented?
3. **Scope:** Which languages, topics, participants, and time periods are included?
4. **Quality:** Are messages complete, duplicated, corrupted, or inconsistently labeled?
5. **Risks:** Could the data contain personal information, harmful content, or other sensitive material?
6. **Evaluation needs:** Is there a suitable held-out set, and does it overlap with training data?

Once you understand the source, convert a small sample into the format required by your tools. Inspect the result before processing the full collection. This helps catch role mapping errors, missing messages, encoding problems, and other issues early.

## Suggested data format

A consistent internal format makes it easier to compare and combine datasets. The following fields are a useful baseline:

| Field | Description |
| --- | --- |
| `conversation_id` | A stable identifier for the conversation. |
| `messages` | An ordered list of messages. |
| `messages[].role` | The speaker or message type, such as `user`, `assistant`, or `system`. |
| `messages[].content` | The message text or structured content. |
| `metadata` | Optional information such as language, source, license, or annotations. |

Keep source-specific fields when they may matter later. For example, a dataset’s original identifier can help trace an example back to its source, while annotation fields may be needed for evaluation. If you transform or remove fields, document what changed and why.

For large collections, newline-delimited JSON is one practical storage option: each line contains one complete conversation. It can be processed incrementally without loading the entire dataset into memory. Other formats may be more suitable depending on your storage and processing tools.

## Preparing a dataset

A typical preparation workflow includes the following steps.

### Inspect

Review both aggregate statistics and individual examples. Useful measurements include conversation count, message count, conversation length, language distribution, and the proportion of missing or empty fields.

Look at examples from across the dataset, including unusually short and long conversations. Averages alone can hide formatting errors or unusual subsets.

### Normalize

Map source fields to a consistent schema while preserving the original meaning. Role labels deserve particular attention: a source’s `speaker_1` and `speaker_2` do not necessarily correspond to `user` and `assistant`.

Record transformations so that another person can reproduce them. Avoid silently changing message order or discarding context.

### Clean

Depending on your use case, cleaning may include removing malformed records, correcting encoding issues, filtering empty messages, and identifying duplicates. Keep a record of the rules applied and the number of examples affected.

Filtering can change the distribution of a dataset. For example, removing very short exchanges may also remove valid greetings or concise answers. Review samples before and after applying a rule.

### Split

Create training, validation, and test splits at the conversation level so that messages from the same conversation do not appear across multiple splits. Where relevant, also consider grouping related conversations by source, participant, or document to reduce overlap.

Choose a splitting strategy that reflects the intended use. A random split can be useful for some experiments, while a time-based or source-based split may better test performance on future or unfamiliar data. Document the strategy and any random seed used.

### Validate

After processing, check that records conform to the expected schema and that identifiers, roles, and message order are intact. Compare counts before and after each major step, and inspect a sample of the final output.

Validation should also cover task-specific requirements. For example, a response-generation task may require each training example to end with an assistant response, while a classification task may require an annotation for every conversation.

## Documentation and provenance

Each dataset or derived collection should have a short data card that answers:

- What does the dataset contain, and what was it created for?
- How was the data collected or generated?
- What transformations and filters were applied?
- What are the known limitations and potential sources of bias?
- What license and usage restrictions apply?
- Who maintains the collection, and how can issues be reported?

Keep the source version and processing details alongside the resulting data. Reproducible provenance makes it easier to investigate problems, update a collection, and compare experimental results.

## Responsible use

Conversation data can contain private information, biased language, unsafe requests, and inaccurate statements. Treat the presence of data in a collection as a reason to inspect it, not as evidence that it is appropriate for every use.

Apply safeguards appropriate to the source and intended application. These may include access controls, personal information detection and removal, content review, and restrictions on redistribution. Automated filters can miss sensitive material and can also remove legitimate examples, so assess their performance where possible.

When reporting results, describe the datasets and processing choices that shaped them. A model evaluated on one conversational setting may perform differently in another.

## Contributing

Contributions that improve dataset documentation, examples, processing guidance, and quality checks are welcome. When proposing a new dataset or change, include enough context for others to assess the source, intended use, licensing, and any known limitations.

Please avoid submitting personal, confidential, or otherwise restricted conversation data without authorization. If you discover a privacy or security concern, report it privately to the project maintainers rather than posting sensitive examples publicly.

## License

The license for this project and the licenses of any datasets used with it should be documented separately. A project license does not automatically grant rights to third-party data. Review the applicable terms for each collection before use or redistribution.
