This pull request adds reusable batch processing for paginated API responses. It allows clients to retrieve multiple pages concurrently, reducing the need for callers to manage pagination themselves.

The new `batch` package provides `ProcessInConcurrentBatches`, which accepts a getter to retrieve each page and a processor to handle its results. Callers can configure the maximum batch size and number of concurrent workers. Getter calls run concurrently, while processor calls are protected by a lock so that only one executes at a time.

The dataset and filter API clients use this functionality to retrieve dimension options. Callers can either collect all options with `GetOptionsInBatches` or supply their own processor with `GetOptionsBatchProcess`. The latter supports handling results as each batch arrives and allows the processor to stop early when appropriate.

If a getter or processor returns an error, processing is aborted and the error is returned to the caller. A processor can also request an early stop without returning an error.

The change provides a shared approach that other clients can use for paginated endpoints, while giving callers control over request size, concurrency and how results are handled.

[Repository documentation](https://github.com/ONSdigital/dp-api-clients-go#batch-processing)
