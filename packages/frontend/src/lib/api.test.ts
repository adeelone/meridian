import { expect, test } from "vitest";
import { normalizeDomain } from "./api";

test("normalizes client domain chips", () => {
  expect(normalizeDomain("https://www.tiktok.com")).toBe("tiktok.com");
});
