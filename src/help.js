import fs from 'fs-extra';
import path from 'path';
import chalk from 'chalk';

export async function help(topic) {
  console.log(chalk.cyan('\n🎯 Hazn Help\n'));

  if (!topic) {
    // Check project state and give contextual advice
    const hasHazn = await fs.pathExists('.hazn');
    
    if (!hasHazn) {
      console.log('Hazn is not installed in this project.\n');
      console.log('Run ' + chalk.yellow('npx hazn install') + ' to get started.\n');
      return;
    }

    const hasStrategy = await fs.pathExists('.hazn/outputs/strategy.md');
    const hasUX = await fs.pathExists('.hazn/outputs/ux-blueprint.md');
    const hasWireframes = await fs.pathExists('.hazn/outputs/wireframes/');
    const hasDev = await fs.pathExists('src/') || await fs.pathExists('app/');

    console.log(chalk.bold('Current State:\n'));
    console.log(`  Strategy:   ${hasStrategy ? chalk.green('✓ Complete') : chalk.yellow('○ Not started')}`);
    console.log(`  UX/Blueprints: ${hasUX ? chalk.green('✓ Complete') : chalk.yellow('○ Not started')}`);
    console.log(`  Wireframes: ${hasWireframes ? chalk.green('✓ Complete') : chalk.yellow('○ Not started')}`);
    console.log(`  Development: ${hasDev ? chalk.green('✓ In progress') : chalk.yellow('○ Not started')}`);

    console.log(chalk.bold('\nRecommended Next Step:\n'));
    
    if (!hasStrategy) {
      console.log('  Start with strategy to define positioning and goals:');
      console.log(chalk.yellow('\n  /hazn-strategy\n'));
      console.log('  This will guide you through:');
      console.log('  • Target audience definition');
      console.log('  • Competitive positioning');
      console.log('  • Value proposition development');
      console.log('  • Content strategy foundations\n');
    } else if (!hasUX) {
      console.log('  Define page architecture and user journeys:');
      console.log(chalk.yellow('\n  /hazn-ux\n'));
    } else if (!hasWireframes) {
      console.log('  Create wireframes to validate layout before coding:');
      console.log(chalk.yellow('\n  /hazn-wireframe\n'));
    } else {
      console.log('  Ready to build! Start development:');
      console.log(chalk.yellow('\n  /hazn-dev\n'));
    }

    return;
  }

  // Topic-specific help
  const topics = {
    'website': `
${chalk.bold('Full Website Workflow')}

The complete path from strategy to deployed website:

1. ${chalk.cyan('/hazn-strategy')} — Define positioning, audience, goals
2. ${chalk.cyan('/hazn-ux')} — Page blueprints and information architecture  
3. ${chalk.cyan('/hazn-copy')} — Conversion-focused messaging
4. ${chalk.cyan('/hazn-wireframe')} — Visual layout validation
5. ${chalk.cyan('/hazn-dev')} — Next.js + Payload CMS implementation
6. ${chalk.cyan('/hazn-seo')} — Technical optimization
7. ${chalk.cyan('/hazn-content')} — Blog and content creation

Each step produces artifacts in .hazn/outputs/ that inform the next step.
`,
    'audit': `
${chalk.bold('Site Audit Workflow')}

Comprehensive analysis for existing websites:

${chalk.cyan('/hazn-audit')} runs four specialized audits:

1. ${chalk.bold('Conversion Audit')} — CRO analysis, funnel optimization
2. ${chalk.bold('Copy Audit')} — Messaging, headlines, CTAs
3. ${chalk.bold('Visual Audit')} — UI/UX, hierarchy, accessibility  
4. ${chalk.bold('SEO Audit')} — Technical SEO, content gaps

Produces a branded HTML report with recommendations.
`,
    'agents': `
${chalk.bold('Available Agents')}

${chalk.cyan('Strategist')}
  Market research, positioning, competitive analysis
  
${chalk.cyan('UX Architect')}  
  Page blueprints, user journeys, conversion flows

${chalk.cyan('Copywriter')}
  Headlines, value props, CTAs, full page copy

${chalk.cyan('Wireframer')}
  Mid-fidelity layouts, responsive design validation

${chalk.cyan('Developer')}
  Next.js, Payload CMS, Tailwind implementation

${chalk.cyan('SEO Specialist')}
  Technical SEO, schema markup, content optimization

${chalk.cyan('Content Writer')}
  Blog posts, keyword-optimized articles

${chalk.cyan('Auditor')}
  Multi-dimensional site analysis
`,
  };

  if (topics[topic]) {
    console.log(topics[topic]);
  } else {
    console.log(`Unknown topic: ${topic}\n`);
    console.log('Available topics: website, audit, agents\n');
  }
}
