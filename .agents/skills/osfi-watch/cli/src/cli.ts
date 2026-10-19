#!/usr/bin/env bun
/**
 * osfi-watch: list and keyword-search OSFI announcements.
 * Zero runtime dependencies. Parses the server-rendered news feed at
 * https://www.osfi-bsif.gc.ca/en/news
 *
 * Parsing anchors (re-pin if the markup changes):
 * - each item: <article class="news feed ..."> ... </article>
 * - title + URL: the heading link inside the article
 * - date: a datetime="YYYY-MM-DD..." attribute inside the article
 */

const BASE = "https://www.osfi-bsif.gc.ca";
const NEWS_URL = `${BASE}/en/news`;
const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36";

interface Item {
  company: null;
  signal: string;
  url: string;
  date: string | null;
  type: string | null;
  source: "osfi-watch";
}

function fail(message: string, code = "fetch_error"): never {
  console.error(JSON.stringify({ error: message, code }));
  process.exit(1);
}

async function getHtml(url: string): Promise<string> {
  let res: Response;
  try {
    res = await fetch(url, {
      headers: { "User-Agent": UA, "Accept-Language": "en-CA,en;q=0.9" },
    });
  } catch (e) {
    fail(`network error fetching ${url}: ${e}`, "network_error");
  }
  if (!res!.ok) fail(`HTTP ${res!.status} fetching ${url}`, "http_error");
  return await res!.text();
}

function stripTags(s: string): string {
  return s
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function parseList(html: string): Item[] {
  const items: Item[] = [];
  const blocks = html.match(/<article class="news feed[\s\S]*?<\/article>/g) ?? [];
  for (const b of blocks) {
    const m = b.match(/<h[23][^>]*>[\s\S]*?<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/);
    if (!m) continue;
    const href = m[1];
    const url = href.startsWith("http") ? href : BASE + href;
    const title = stripTags(m[2]);
    if (!title) continue;
    const d = b.match(/datetime="(\d{4}-\d{2}-\d{2})/);
    const typeSection = b.match(/field--name-field-news-type[\s\S]{0,600}?field--item">([^<]{2,80})</);
    items.push({
      company: null,
      signal: title,
      url,
      date: d ? d[1] : null,
      type: typeSection ? stripTags(typeSection[1]) : null,
      source: "osfi-watch",
    });
  }
  return items;
}

async function fetchDetail(url: string): Promise<{ title: string; snippet: string }> {
  const html = await getHtml(url);
  const titleM = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/);
  const title = titleM ? stripTags(titleM[1]) : url;
  // Prefer the Drupal body field; fall back to the main element.
  const bodyM =
    html.match(/field--name-body[\s\S]*?field__item[^>]*>([\s\S]*?)<\/div>\s*<\/div>/) ??
    html.match(/<main[\s\S]*?>([\s\S]*?)<\/main>/);
  const text = bodyM ? stripTags(bodyM[1]) : "";
  return { title, snippet: text.slice(0, 1500) };
}

function printTable(items: Item[]): void {
  for (const it of items) {
    console.log(`${it.date ?? "no-date"}\t${it.type ?? "-"}\t${it.signal}\n  ${it.url}`);
  }
}

function usage(): never {
  console.error(`osfi-watch: list and search OSFI announcements

Usage:
  cli.ts list [--page <n>] [--limit <n>] [--format json|table]
  cli.ts search --query "<kw1, kw2>" [--since <YYYY-MM-DD>] [--limit <n>] [--format json|table]
  cli.ts detail <url> [--format json|plain]`);
  process.exit(1);
}

function flag(args: string[], name: string): string | null {
  const i = args.findIndex((a) => a === `--${name}`);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : null;
}

async function main(): Promise<void> {
  const [cmd, ...args] = Bun.argv.slice(2);
  if (!cmd) usage();
  const format = flag(args, "format") ?? "json";
  const limitRaw = flag(args, "limit");
  const limit = limitRaw ? parseInt(limitRaw, 10) : 20;

  if (cmd === "list" || cmd === "search") {
    const page = flag(args, "page");
    const url = page && page !== "0" ? `${NEWS_URL}?page=${page}` : NEWS_URL;
    const html = await getHtml(url);
    let items = parseList(html);

    if (cmd === "search") {
      const query = flag(args, "query") ?? flag(args, "q");
      if (!query) fail("--query is required for search", "bad_args");
      const terms = query!
        .split(",")
        .map((t) => t.trim().toLowerCase())
        .filter(Boolean);
      items = items.filter((it) => {
        const hay = `${it.signal} ${it.type ?? ""}`.toLowerCase();
        return terms.some((t) => hay.includes(t));
      });
      const since = flag(args, "since");
      if (since) items = items.filter((it) => it.date !== null && it.date >= since);
    }

    items = items.slice(0, limit);
    if (format === "table") printTable(items);
    else console.log(JSON.stringify({ results: items }, null, 2));
    return;
  }

  if (cmd === "detail") {
    const url = args[0];
    if (!url || url.startsWith("--")) usage();
    const { title, snippet } = await fetchDetail(url);
    if (format === "plain") {
      console.log(title + "\n\n" + snippet);
    } else {
      console.log(JSON.stringify({ title, url, snippet, source: "osfi-watch" }, null, 2));
    }
    return;
  }

  usage();
}

main().catch((e) => fail(String(e), "unexpected"));
