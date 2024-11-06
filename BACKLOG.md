### TODO List

- [ ] **Implement Retry Logic in `handle` Method**
  - Add retry logic in the `handle` method for cases where `drain_events` fails. 
  - Optionally, clean up or explicitly close the consumer after each `drain_events` call to manage resources effectively.

- [ ] **Explicitly Clean Up Consumer After Use**
  - Ensure the consumer is properly closed or reset after processing to avoid potential issues if `handle` is called multiple times.
  - If `self.consumer` is reused across calls, confirm it’s reset or released as needed.

- [ ] **Add Error Handling for Lazy Initialization in `producer` and `consumer`**
  - Include basic error handling when initializing `self.producer` and `self.consumer` properties to catch potential `ConnectionError`s or channel creation issues.
  - Log any initialization errors clearly for better debugging.

- [ ] **Replace All `print` Statements with Logging**
  - Replace all `print` statements in the `AmqpCLI` and other CLI classes with `logging` statements.
  - Use appropriate log levels (`logging.info()`, `logging.warning()`, `logging.error()`) to categorize log messages.

- [ ] **Make Prefetch Count Configurable**
  - Replace the hardcoded prefetch count of `5` with a configurable setting.
  - Use the `BATCH_SIZE` environment variable to set `self.prefetch_count`, defaulting to `1` if `BATCH_SIZE` is not defined.
  - Log a warning if `BATCH_SIZE` is unset, indicating that the prefetch count defaults to `1`.

### Minor Adjustments

- [ ] **Use `logging.info` to Output Key Steps and Configurations**
  - Add log entries at key steps such as starting protocols, configurations loaded, and after each critical action (e.g., after publishing a message).
  - This will improve traceability and monitoring of the application flow, especially in production.

- [ ] **Convert Configuration-Dependent Variables**
  - Ensure variables such as `routing_keys`, `exchange_name`, and `queue_name` are only populated from configuration settings, to keep the `AmqpCLI` class flexible for different environments.