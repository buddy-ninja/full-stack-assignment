import { expect, test } from "bun:test";
import type { Sql } from "postgres";
import { createApp } from "../src/app";

test("health responds without a database", async () => {
  const app = createApp({ sql: {} as Sql });
  const res = await app.handle(new Request("http://localhost/health"));
  expect(await res.json()).toEqual({ status: "ok" });
});
