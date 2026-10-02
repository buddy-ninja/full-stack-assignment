import { Elysia } from "elysia";
import type { Sql } from "postgres";

export const createApp = (deps: { sql: Sql }) =>
  new Elysia()
    .get("/health", () => ({ status: "ok" }))
    .get("/health/db", async () => {
      const [{ pets }] = await deps.sql<{ pets: number }[]>`select count(*)::int as pets from pets`;
      return { status: "ok", pets };
    });

// Your routes go here.
