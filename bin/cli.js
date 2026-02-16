#!/usr/bin/env node

import { Command } from 'commander';
import { install } from '../src/installer.js';
import { help } from '../src/help.js';
import chalk from 'chalk';

const program = new Command();

program
  .name('hazn')
  .description(chalk.cyan('🎯 Hazn') + ' — AI-driven marketing website development framework')
  .version('0.1.0');

program
  .command('install')
  .description('Install Hazn into your project')
  .option('-d, --directory <path>', 'Target directory', '.')
  .option('-y, --yes', 'Skip prompts and use defaults')
  .option('--tools <tools>', 'AI tools to configure (claude-code,cursor,windsurf)', 'claude-code')
  .option('--workflows <workflows>', 'Workflows to install (all,website,audit,blog)', 'all')
  .action(install);

program
  .command('help [topic]')
  .description('Get contextual help on what to do next')
  .action(help);

program
  .command('list')
  .description('List available agents and workflows')
  .action(() => {
    console.log(chalk.cyan('\n🎯 Hazn Agents:\n'));
    console.log('  • Strategist    — Market positioning & competitive analysis');
    console.log('  • UX Architect  — Page blueprints & user journey design');
    console.log('  • Copywriter    — Conversion-focused messaging');
    console.log('  • Wireframer    — Mid-fidelity layout validation');
    console.log('  • Developer     — Next.js + Payload CMS implementation');
    console.log('  • SEO Spec      — Technical SEO & content optimization');
    console.log('  • Auditor       — Conversion, copy, and visual audits');
    
    console.log(chalk.cyan('\n📋 Workflows:\n'));
    console.log('  • /hazn-website — Full website build (strategy → deploy)');
    console.log('  • /hazn-audit   — Comprehensive site audit');
    console.log('  • /hazn-blog    — SEO blog content pipeline');
    console.log('  • /hazn-landing — Single landing page (fast path)');
    console.log('  • /hazn-help    — Contextual guidance\n');
  });

program.parse();
