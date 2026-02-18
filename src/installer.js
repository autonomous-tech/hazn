import fs from 'fs-extra';
import path from 'path';
import { fileURLToPath } from 'url';
import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PACKAGE_ROOT = path.resolve(__dirname, '..');

export async function install(options) {
  console.log(chalk.cyan('\n🎯 Hazn Installer\n'));
  console.log('AI-driven marketing website development framework\n');

  const targetDir = path.resolve(options.directory);

  // Interactive prompts unless --yes
  let config = {
    tools: options.tools.split(','),
    workflows: options.workflows === 'all' 
      ? ['website', 'audit', 'blog', 'landing'] 
      : options.workflows.split(','),
    includeSkills: true,
    includeTemplates: true,
  };

  if (!options.yes) {
    const answers = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'tools',
        message: 'Which AI tools are you using?',
        choices: [
          { name: 'Claude Code', value: 'claude-code', checked: true },
          { name: 'Cursor', value: 'cursor' },
          { name: 'Windsurf', value: 'windsurf' },
          { name: 'Other (manual setup)', value: 'other' },
        ],
      },
      {
        type: 'checkbox',
        name: 'workflows',
        message: 'Which workflows do you need?',
        choices: [
          { name: 'Full Website Build', value: 'website', checked: true },
          { name: 'Site Audit', value: 'audit', checked: true },
          { name: 'Blog Content Pipeline', value: 'blog', checked: true },
          { name: 'Landing Page (fast)', value: 'landing', checked: true },
        ],
      },
      {
        type: 'confirm',
        name: 'includeSkills',
        message: 'Include full skill definitions?',
        default: true,
      },
    ]);
    config = { ...config, ...answers };
  }

  const spinner = ora('Installing Hazn...').start();

  try {
    // Create .hazn directory
    const haznDir = path.join(targetDir, '.hazn');
    await fs.ensureDir(haznDir);
    await fs.ensureDir(path.join(haznDir, 'agents'));
    await fs.ensureDir(path.join(haznDir, 'workflows'));
    await fs.ensureDir(path.join(haznDir, 'skills'));
    await fs.ensureDir(path.join(haznDir, 'outputs'));

    spinner.text = 'Copying agents...';
    await fs.copy(
      path.join(PACKAGE_ROOT, 'agents'),
      path.join(haznDir, 'agents')
    );

    spinner.text = 'Copying workflows...';
    await fs.copy(
      path.join(PACKAGE_ROOT, 'workflows'),
      path.join(haznDir, 'workflows')
    );

    if (config.includeSkills) {
      spinner.text = 'Copying skills...';
      await fs.copy(
        path.join(PACKAGE_ROOT, 'skills'),
        path.join(haznDir, 'skills')
      );
    }

    spinner.text = 'Writing configuration...';
    await fs.writeJson(path.join(haznDir, 'config.json'), {
      version: '0.1.0',
      tools: config.tools,
      workflows: config.workflows,
      installedAt: new Date().toISOString(),
    }, { spaces: 2 });

    // Copy HAZN.md to project root
    await fs.copy(
      path.join(PACKAGE_ROOT, 'templates', 'HAZN.md'),
      path.join(targetDir, 'HAZN.md')
    );

    // Tool-specific setup
    if (config.tools.includes('claude-code')) {
      spinner.text = 'Configuring Claude Code...';
      await setupClaudeCode(targetDir, haznDir);
    }

    if (config.tools.includes('cursor')) {
      spinner.text = 'Configuring Cursor...';
      await setupCursor(targetDir, haznDir);
    }

    spinner.succeed(chalk.green('Hazn installed successfully!'));

    console.log(chalk.cyan('\n📁 Created:\n'));
    console.log(`  ${targetDir}/`);
    console.log('  ├── HAZN.md              — Quick reference');
    console.log('  ├── .claude/commands/    — Slash commands (/hazn-*)');
    console.log('  └── .hazn/');
    console.log('      ├── agents/          — Agent personas');
    console.log('      ├── workflows/       — Workflow definitions');
    console.log('      ├── skills/          — Domain skills');
    console.log('      └── outputs/         — Generated artifacts\n');

    console.log(chalk.cyan('🚀 Next steps:\n'));
    console.log('  1. Open this folder in Claude Code / Cursor / Windsurf');
    console.log('  2. Run ' + chalk.yellow('/hazn-help') + ' to get started');
    console.log('  3. Or jump straight to ' + chalk.yellow('/hazn-website') + ' for a full build\n');

  } catch (error) {
    spinner.fail(chalk.red('Installation failed'));
    console.error(error);
    process.exit(1);
  }
}

async function setupClaudeCode(targetDir, haznDir) {
  // Create .claude/commands/ for custom slash commands
  const commandsDir = path.join(targetDir, '.claude', 'commands');
  await fs.ensureDir(commandsDir);

  // Define commands and their prompts
  const commands = {
    'hazn-help': `Check the .hazn/outputs/ directory to see what artifacts exist (strategy.md, ux-blueprint.md, copy/, wireframes/).

Based on what exists, recommend the next logical step:
- If nothing exists → suggest /hazn-strategy
- If strategy.md exists but no ux-blueprint.md → suggest /hazn-ux  
- If ux-blueprint.md exists but no copy/ → suggest /hazn-copy
- If copy exists but no wireframes/ → suggest /hazn-wireframe
- If wireframes exist → suggest /hazn-dev

Show current state and give clear guidance on what to do next.`,

    'hazn-strategy': `Read .hazn/agents/strategist.md and follow its instructions exactly.

You are now the Strategist agent. Guide the user through strategic foundations for their website.`,

    'hazn-ux': `Read .hazn/agents/ux-architect.md and follow its instructions exactly.

You are now the UX Architect agent. Create page blueprints and information architecture.`,

    'hazn-copy': `Read .hazn/agents/copywriter.md and follow its instructions exactly.

You are now the Copywriter agent. Write conversion-focused copy for the website.`,

    'hazn-wireframe': `Read .hazn/agents/wireframer.md and follow its instructions exactly.

You are now the Wireframer agent. Create mid-fidelity wireframes for layout validation.`,

    'hazn-dev': `Read .hazn/agents/developer.md and follow its instructions exactly.

You are now the Developer agent. Build with Next.js + Payload CMS + Tailwind.`,

    'hazn-seo': `Read .hazn/agents/seo-specialist.md and follow its instructions exactly.

You are now the SEO Specialist agent. Handle technical SEO and content optimization.`,

    'hazn-content': `Read .hazn/agents/content-writer.md and follow its instructions exactly.

You are now the Content Writer agent. Create SEO-optimized blog posts and articles.`,

    'hazn-audit': `Read .hazn/agents/auditor.md and follow its instructions exactly.

You are now the Auditor agent. Perform multi-dimensional website analysis.`,

    'hazn-website': `Read .hazn/workflows/website.yaml to understand the full website build workflow.

Guide the user through the complete process: Strategy → UX → Copy → Wireframe → Dev → SEO`,

    'hazn-landing': `Read .hazn/workflows/landing.yaml to understand the landing page workflow.

Guide the user through the fast path for a single landing page.`,
  };

  // Write each command file
  for (const [name, content] of Object.entries(commands)) {
    await fs.writeFile(path.join(commandsDir, `${name}.md`), content);
  }

  // Add to CLAUDE.md if it exists, or create it
  const claudeMdPath = path.join(targetDir, 'CLAUDE.md');
  const haznInclude = `
## Hazn Framework

This project uses Hazn for AI-driven marketing website development.

### Model Preference

Always use the most capable available model (e.g., claude-sonnet-4, opus) for Hazn workflows unless the user specifies otherwise. Quality and reasoning matter more than speed for marketing website development.

### Core Behavior: Plan → Approve → Build

**Always follow this pattern:**

1. **Plan first** — Before building anything, propose a plan (structure, sections, approach)
2. **Wait for approval** — Don't proceed until the user confirms or adjusts
3. **Build incrementally** — Work in chunks, show progress after each major piece
4. **Checkpoint** — After each section/component, pause for review before continuing

Never go off and build an entire page silently. Show your work, get feedback, iterate.

**Example flow:**

User: "Build me a pricing page with 3 tiers"

You: "Here's my plan:
1. Hero with headline + subhead
2. Pricing cards (3 tiers)  
3. Feature comparison table
4. FAQ section
5. CTA banner

Tech: React component, Tailwind, [conventions from project]

Want me to proceed with this structure?"

User: "Yes, but skip the FAQ"

You: "Got it. Starting with the hero section... [shows code]. Hero done. Continue to pricing cards?"

### Slash Commands

Hazn registers these commands in \`.claude/commands/\`:

- \`/hazn-help\` — Check progress and get next step recommendation
- \`/hazn-strategy\` — Run Strategist agent
- \`/hazn-ux\` — Run UX Architect agent
- \`/hazn-copy\` — Run Copywriter agent
- \`/hazn-wireframe\` — Run Wireframer agent
- \`/hazn-dev\` — Run Developer agent
- \`/hazn-seo\` — Run SEO Specialist agent
- \`/hazn-content\` — Run Content Writer agent
- \`/hazn-audit\` — Run Auditor agent
- \`/hazn-website\` — Full website workflow
- \`/hazn-landing\` — Landing page workflow

### Key Directories

- \`.hazn/agents/\` — Agent persona definitions (read when triggered)
- \`.hazn/workflows/\` — Workflow definitions
- \`.hazn/skills/\` — Deep domain knowledge (reference as needed)
- \`.hazn/outputs/\` — Generated artifacts (strategy.md, ux-blueprint.md, etc.)

See HAZN.md for quick reference.
`;

  if (await fs.pathExists(claudeMdPath)) {
    const existing = await fs.readFile(claudeMdPath, 'utf-8');
    if (!existing.includes('Hazn Framework')) {
      await fs.appendFile(claudeMdPath, haznInclude);
    }
  } else {
    await fs.writeFile(claudeMdPath, `# CLAUDE.md\n${haznInclude}`);
  }
}

async function setupCursor(targetDir, haznDir) {
  // Create .cursorrules if it doesn't exist
  const cursorRulesPath = path.join(targetDir, '.cursorrules');
  const haznRules = `
# Hazn Framework
This project uses Hazn for AI-driven website development.
Load agents from .hazn/agents/ when invoking /hazn-* commands.
Follow workflows in .hazn/workflows/ for structured processes.
`;

  if (await fs.pathExists(cursorRulesPath)) {
    const existing = await fs.readFile(cursorRulesPath, 'utf-8');
    if (!existing.includes('Hazn Framework')) {
      await fs.appendFile(cursorRulesPath, haznRules);
    }
  } else {
    await fs.writeFile(cursorRulesPath, haznRules);
  }
}
