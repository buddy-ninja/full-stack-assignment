import postgres from "postgres";
import { createApp } from "./app";

const sql = postgres(process.env.DATABASE_URL ?? "postgres://ninja:ninja@localhost:5432/ninja");
const port = Number(process.env.PORT ?? 3000);

createApp({ sql }).listen(port);
console.log(`gateway listening on :${port}`);
