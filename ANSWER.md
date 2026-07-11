# Answer Design

Meridian retrieves sources with `search_and_contents`, builds numbered passages, and asks an `LLMProvider` to answer only from those passages. The default provider is extractive so the product works without a second API key.

After synthesis, Meridian scans citation markers such as `[1]` and verifies that every number maps to a supplied source. If a provider cites a nonexistent source, Meridian regenerates once with a corrective instruction. If the second response is still invalid, the answer is returned with a visible warning.
