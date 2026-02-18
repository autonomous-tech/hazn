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
    console.log('  ├── HAZN.md          — Quick reference & commands');
    console.log('  └── .hazn/');
    console.log('      ├── agents/      — Agent personas');
    console.log('      ├── workflows/   — Workflow definitions');
    console.log('      ├── skills/      — Domain skills');
    console.log('      └── outputs/     — Generated artifacts\n');

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
  // Add to CLAUDE.md if it exists, or create it
  const claudeMdPath = path.join(targetDir, 'CLAUDE.md');
  const haznInclude = `
## Hazn Framework

This project uses Hazn for AI-driven marketing website development.

### Trigger Handling

When the user types any of these triggers, read the corresponding agent file and follow its instructions:

| Trigger | Agent File |
|---------|------------|
| \`/hazn-help\` | Check \`.hazn/outputs/\` state and recommend next step |
| \`/hazn-strategy\` | Read \`.hazn/agents/strategist.md\` and follow it |
| \`/hazn-ux\` | Read \`.hazn/agents/ux-architect.md\` and follow it |
| \`/hazn-copy\` | Read \`.hazn/agents/copywriter.md\` and follow it |
| \`/hazn-wireframe\` | Read \`.hazn/agents/wireframer.md\` and follow it |
| \`/hazn-dev\` | Read \`.hazn/agents/developer.md\` and follow it |
| \`/hazn-seo\` | Read \`.hazn/agents/seo-specialist.md\` and follow it |
| \`/hazn-content\` | Read \`.hazn/agents/content-writer.md\` and follow it |
| \`/hazn-audit\` | Read \`.hazn/agents/auditor.md\` and follow it |
| \`/hazn-website\` | Read \`.hazn/workflows/website.yaml\` for full workflow |
| \`/hazn-landing\` | Read \`.hazn/workflows/landing.yaml\` for landing page workflow |

### /hazn-help Behavior

When user types \`/hazn-help\`:
1. Check what exists in \`.hazn/outputs/\` (strategy.md, ux-blueprint.md, copy/, wireframes/)
2. Recommend the next logical step based on what's missing
3. If nothing exists, start with \`/hazn-strategy\`

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
