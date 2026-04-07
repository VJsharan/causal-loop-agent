const { query } = require("gitclaw");

async function runDemo() {
  console.log("=== Running Past Demo (repo-autopsy) ===\n");
  const pastPrompt = "Execute the `repo-autopsy` skill on the `dummy_repo/` directory. Write your findings to autopsy-report.md.";
  
  for await (const msg of query({
    prompt: pastPrompt,
    dir: "./"
  })) {
    if (msg.type === "delta" && msg.content) {
      process.stdout.write(msg.content);
    }
  }

  console.log("\n\n=== Running Present Demo (mortem-interrogator) ===\n");
  const presentPrompt = "Execute the `mortem-interrogator` skill. Read `incident.md` and output your verdict to `systemic-finding.md`.";
  
  for await (const msg of query({
    prompt: presentPrompt,
    dir: "./"
  })) {
    if (msg.type === "delta" && msg.content) {
      process.stdout.write(msg.content);
    }
  }
  
  console.log("\n\n=== Demo Complete ===");
}

runDemo().catch(console.error);
