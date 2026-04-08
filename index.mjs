/**
 * CausalLoop — ESM entry point
 *
 * This file exists for ESM-first environments and gitagent SDK compatibility.
 * It re-exports everything from index.js and can be used directly:
 *
 *   import { runRepoAutopsy } from './index.mjs';
 *
 * Or invoked via gitclaw:
 *   gitclaw --dir . "scan this repo for hardcoded credentials"
 *
 * For the full feature set, use the main entry point:
 *   node index.js
 */

// Re-export identity: this module is the same as index.js.
// Both index.js and index.mjs are native ESM (package.json "type": "module").
export * from "./index.js";
